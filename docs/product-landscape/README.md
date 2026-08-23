# Product landscape

Three notes from one pass, 2026-08-22. They answer a chain of questions rather than three separate
ones, and read in this order.

| Note | Question | Size |
|---|---|---|
| [2026-08-22-product-comparison-verified.md](2026-08-22-product-comparison-verified.md) | What else exists, and where do we stand against it? | ~2,460 lines |
| [2026-08-22-memoria-and-knowledge-harness.md](2026-08-22-memoria-and-knowledge-harness.md) | How do we stand against our own other implementation of the same thesis? | ~215 lines |
| [2026-08-22-assembled-harness-spec.md](2026-08-22-assembled-harness-spec.md) | Could this be assembled from existing parts instead — and given that it exists, what stays, what is ported, what is replaced? | ~580 lines |

## The evidence rule they share

Roster names came from `research/`; every fact was re-derived from the GitHub API, a clone read
directly, a primary specification, or a paper in `sources/`. Claims cite the file and line that
produced them. Read depth is marked per row — a file was opened, or the row rests on repository
metadata.

That rule caught real errors, several of them ours: seven licences recorded as absent that were
declared in READMEs, four absences asserted about Memoria that reading falsified, and three claims
this repository held about its own uniqueness that competitors already implement. Corrections are
recorded in place rather than in a changelog, and the method notes in the comparison's §1 and §19.3
exist because of them.

## What they conclude

**Build the trust core, adopt the breadth** — reached three times by different routes. The
comparison gets there from a capability survey (§17.2), the assembled spec from a
component-by-component audit (§8), and the two-projects note from the observation that the closest
comparable is in-house.

Two qualifications carry more weight than the conclusion. The literature (comparison §8.5) finds
that **false-positive rate, not recall, decides whether a verifier is deployable** — and neither of
our projects has measured one. And the ownership calculus **inverts between code and skills**
(assembled spec §9.2): a code fork is cheap to hold because tests keep it still, while a skill is
prose with no test that catches drift, so third-party skills are worth more than third-party
libraries.
