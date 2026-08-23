# Product landscape

Four notes from one pass, 2026-08-22, divided by **lifecycle** rather than by the order they were
written. Each has a different update cadence, and that is why they are separate files.

| Note | Question | Updates | Size |
|---|---|---|---|
| [product-comparison-verified](2026-08-22-product-comparison-verified.md) | What exists, and where do we stand against it? | when the field moves — §19 is the re-run protocol | 2,092 |
| [memoria-and-knowledge-harness](2026-08-22-memoria-and-knowledge-harness.md) | How do we stand against our own other implementation of the same thesis? | when Memoria moves, which is daily | 223 |
| [adoption-plan](2026-08-22-adoption-plan.md) | Does the product have a place, what is adoptable, and what changes in this tree? | as we act on it | 741 |
| [assembled-harness-spec](2026-08-22-assembled-harness-spec.md) | Could this have been assembled from existing parts instead? | never — a dated thought experiment | 312 |

**The comparison is what was found. The adoption plan is what to do about it.** That split is
deliberate: the first is evidence with a re-run protocol, the second is a decision that changes as
it is executed. They were one document until the positioning verdict, the adoption tiers and the
per-file actions had all been corrected twice in two places.

## The evidence rule they share

Roster names came from `research/`; every fact was re-derived from the GitHub API, a clone read
directly, a primary specification, or a paper in `sources/`. Claims cite the file and line that
produced them. Read depth is marked per row — a file was opened, or the row rests on repository
metadata.

That rule caught real errors, several of them ours: seven licences recorded as absent that were
declared in READMEs, four absences asserted about Memoria that reading falsified, and three claims
this repository held about its own uniqueness that competitors already implement. Corrections are
recorded in place rather than in a changelog, and the method notes at the comparison's §1 and §19.3
exist because of them.

## What they conclude

**Build the trust core, adopt the breadth** — reached three times by different routes: from a
capability survey, from a component-by-component audit, and from the observation that the closest
comparable is in-house.

Two qualifications carry more weight than the conclusion. The literature (comparison §8.5) finds
that **false-positive rate, not recall, decides whether a verifier is deployable**, and neither of
our projects has measured one. And the ownership calculus **inverts between code and skills**
(adoption plan §3.2): a code fork is cheap to hold because tests keep it still, while a skill is
prose with no test that catches drift — so third-party skills are worth more than third-party
libraries, and writing one should need a reason.
