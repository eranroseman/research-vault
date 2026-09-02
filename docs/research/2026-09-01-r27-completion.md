# R27 completion: the four corpora read properly

Research note, 2026-09-01. Completes the competitive analysis begun in `docs/research/2026-09-01-pre-spec-competitive-analysis.md`, whose four remaining corpora had been read as verdict headlines only. Calibrates `docs/superpowers/requirements/2026-09-01-writing-requirements.md`.

**Method.** One isolated agent per corpus, each given the 33-requirement set and its own corpus, told it did not know what else was being read. Every corpus's first four MEASURED ADD or RECALIBRATE findings went to an adversarial verifier instructed to refute — on inexact quotation, wrong clause, secondary-presented-as-primary, over-generalisation, or transfer failure — and to default to refuted where it could not independently confirm. 20 agents.

**Headline: verification killed a third of what was checked.** Sixteen findings were verified; five were refuted outright and one had sub-claims struck. Everything below labelled *survived* was re-read at the named primary by a second agent trying to break it.

______________________________________________________________________

## Survived verification

| #   | Verdict     | Primary                                       | What it says                                                                                                                                                                                                                                                 |
| --- | ----------- | --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| R35 | ADD         | ECSS-E-ST-10-06C 8.2.8a; INCOSE GtWR V3.1 R25 | *"A technical requirement shall be self-contained."* Meaning must not depend on the section heading.                                                                                                                                                         |
| R36 | ADD         | FAA REMH DOT/FAA/AR-08/32 §2.4                | Environmental assumptions get their own section: *"These are actually requirements levied by the system on its environment… Failure to identify the environmental assumptions and the subsequent misuse of the system is a common cause of system failure."* |
| R37 | ADD         | ECSS 7.2.3d; INCOSE C11; FAA REMH 2.8.4–2.8.5 | The set is checked as a set: *"only one ideal value is assigned to each controlled variable"*, and the same term means the same thing throughout.                                                                                                            |
| R38 | ADD         | ECSS 7.2.7a, 8.3.2                            | *"If a clause is stated to be informative or descriptive, then this clause shall not contain any requirement or recommendation."*                                                                                                                            |
| R39 | ADD         | OpenAI Model Spec 2026-08-18                  | Provider behavioural defaults are published at **overridable** authority levels, so silence accepts them. Conditional on the product's user-facing output being model-generated.                                                                             |
| R22 | RECALIBRATE | Anthropic Usage Policy                        | *"Human-in-the-loop: … a qualified professional in that field must review the content or decision prior to dissemination or finalization."* Triggered by use-case class.                                                                                     |
| R24 | RECALIBRATE | PCR 2015 reg 42(13); FAR 11.105, 11.002(c)    | The escape hatch: naming a specific thing is permitted *"on an exceptional basis"*, accompanied by *"or equivalent"*.                                                                                                                                        |
| R25 | RECALIBRATE | FAR 16.603-2(c)                               | A binding instrument may carry an unresolved item, but with a deadline: *"definitization… within 180 days… or before completion of 40 percent of the work, whichever occurs first."*                                                                         |
| R28 | RECALIBRATE | FAR 10.002(c)                                 | Sourcing runs **both ways**: *"agencies shall reevaluate the need… and determine whether the need can be restated"*. Our R28 is a one-way valve.                                                                                                             |

**The AUP finding is the one with teeth.** Anthropic's policy makes *"therapy, mental health"* a High-Risk use case carrying mandatory qualified-professional review and per-session AI disclosure, while carving out *"advice on sleep, stress, nutrition, exercise"*. The line runs through the author's own product category, and no requirement in the set can currently see it.

______________________________________________________________________

## Refuted — not applied

- **A precedence rule between requirements**, from the Model Spec's authority levels. Refuted on transfer: the chain of command orders *instruction sources* (root, developer, user), not two requirements written by one person. Quotes were exact.
- **Rationale as an obligation distinct from source**, from Claude's constitution. Refuted: the constitution explains its reasoning as a stated preference — *"we try to explain any rules we do want Claude to follow"* — not as a requirement on a requirements artifact. The same finding arrived independently from systems-safety and was **not** verified, so it survives only as a lead.
- **A bound glossary as a first-class field**, from the CCS Statement of Requirements template. Refuted on four grounds; the template says *"for the purposes of this procurement"*, and the transfer rests on a dispute between parties.
- **All four verified `testable-at-scale` findings** — worked pass/fail examples at three outcomes (ACT §4.9), R19's disposal half (ACT §4.1), R17's two-level threshold (WCAG A/AA/AAA), and the mandatory/desirable decision rule (WCAG Understanding Conformance). Quotes were exact in every case; all four broke on generalisation or transfer. The corpus's own verifier stated it plainly: *"Do not ADD a mandatory/desirable decision rule on this corpus's authority; it does not publish one."* Nothing from this corpus is applied.

**One sub-claim struck inside a surviving finding.** The R24 escape hatch was argued from *"three independent regimes"*. That is false: PCR 2015, the Procurement Act 2023 and FAR Part 11 all descend from WTO GPA Article X, verified at wto.org. One ancestor, three descendants. The escape hatch survives; the independence claim does not, and the systems-safety corpus supplies the genuinely separate second leg.

**Everything else is a lead, not a finding.** 74 calibrations were returned; 16 were verified. The other 58 — including every systems-safety finding past the first four, and the unverified ADDs from procurement and testable-at-scale — have not been checked against their primaries by a second agent and are **not applied**. Same rule as the first pass. Notable among them, so nobody rediscovers them as new: rationale as an obligation distinct from source, per-requirement classification rather than one class for the whole need, ECSS's four-part header for R29, and ECSS forbidding the aimed-at level inside the requirement, which would break R17.

______________________________________________________________________

## A contamination I introduced

The guard block told every agent: *"A requirement here is by definition a MUST — anything droppable is a goal, not a requirement, and goals live in a separate section."*

**There is no goals section.** The first half is the author's ruling; the second half is mine, and it is false about the artifact. Two findings rest on it — a procurement finding that *"nothing orders the goals against each other"*, and a `testable-at-scale` CONFIRM of the convention — and neither can be trusted, because both were told the structure exists. Recorded rather than quietly dropped: this is the second time in this effort a guard block primed agents toward a shape, after the earlier sweep that named the expected gaps.

______________________________________________________________________

## Predictions checked

Before this ran, two leads were recorded from the headline pass. Both resolve, one against me.

**"FAR runs market research in both directions."** Confirmed, and the clause is 10.002(c) rather than 10.001(a)(2)(i). R28 is genuinely a one-way valve where the primary is two-way.

**"The sourcing screen is mandatory-tier-only, and procurement forbids the mandatory tier standing alone."** Not supported. The corpus's decision rule for the mandatory/desirable split was verified and refuted, and the surviving procurement finding is about ordering goals against each other, which rests on the goals section that does not exist. The gap I predicted is not established by this evidence.

______________________________________________________________________

## Not reached

OpenAI's usage policies returned HTTP 403 to every attempt, so the provider-policy finding is scoped to Anthropic's AUP alone — defensible, since the author's products run on Claude, but no "all providers do this" claim is available. The Model Spec's "detailed policies" are cited by it and not published at that URL. Three papers (Constitutional AI, XSTest, MT-Bench) were read as abstracts only.
