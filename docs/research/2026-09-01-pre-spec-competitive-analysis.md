# Competitive analysis: calibrating the pre-spec requirement set

Research note, 2026-09-01. Calibrates the requirements for `writing-requirements` — see `docs/superpowers/requirements/2026-09-01-writing-requirements.md`.

**Question asked:** how does our requirement set compare to what others require? Not *which product is best* — every verdict is about **our** set: ADD, RECALIBRATE, DROP or CONFIRM.

**Corpora:** regulated health software; published LLM behaviour specifications; systems and safety engineering; product discovery; public procurement; requirement formats written to be tested at scale.

**Status warning.** Two of six dimensions were read in full and folded into the requirements document. **Four were read only as verdict headlines and their findings are not applied.** Everything under "Not yet applied" below is an open item, not a closed one.

______________________________________________________________________

## Applied

### Interview technique — the largest correction

**RECALIBRATE R4, three separate findings, all measured.**

The guess-attached question is a recognised technique in two traditions, but in both the guess is **backward-looking**: Beyer and Holtzblatt's contextual-inquiry *Interpretation* principle has the interviewer state back meaning the person has **already expressed**, as a **statement**, not attached to an unanswered question. The agent-skill rendering that attaches a forward guess to an open question is a mutation of it.

Where a hypothesis must precede an answer, Willis names **single-possibility probing** as the biasing form and **multi-possibility probing** as the remedy — offer the plausible alternatives, not one.

The harm is measured rather than speculative: Pew documents acquiescence bias, **worse with an interviewer present**, and an agent asking questions is an interviewer present. Plus order effects.

*Applied as R5.* The skill this was taken from mitigates only with *"be visibly willing to be wrong"*, which is unevidenced.

**ADD — anchor elicitation in specific past events**, not opinions, generalities or predictions. Three independent primaries converge; the single most-agreed rule in the discovery corpus. *Applied as R6.*

**RECALIBRATE R9 — confirmation is continuous in both traditions that use it** (contextual inquiry's *Interpretation*, qualitative research's *member checking*), not concentrated into one terminal restatement. *Applied: R9 now requires both.*

**RECALIBRATE R10 — a live disagreement, recorded rather than resolved.** Fitzpatrick argues verbal assent is precisely the data type that must not terminate elicitation, and lists *"meetings which went well"* among the symptoms of failure; his replacement is costly commitment. ISO/IEC/IEEE 12207 6.4.2.2(g) makes stakeholder agreement a process outcome. *Applied: the standards position, with the disagreement recorded as an open question.*

**CONFIRM R7 — a null result in our favour.** Nobody caps question count. Every practice caps something adjacent instead: learning goals per person-type, session length, question density.

**CONFIRM R3 ordering, R20, R24** — problem-before-solution is the most consensual structural claim in the corpus, stated as hard ordering by Torres, Fitzpatrick and Cagan independently.

**CONFIRM R11 and R12** — Fitzpatrick imposes a near-exact provenance discipline and gives the reason: *"the artifact's job is to make self-deception harder."*

**ADD — verbatim material marked as verbatim**, distinct from the agent's paraphrase. *Applied as R13.*

### Regulated health software

**ADD — declared risk tier with a recorded rationale.** Every regime in the corpus scales the rigour of requirements work by a declared tier and makes the tier declaration itself a deliverable that never scales down: FDA documentation levels Basic/Enhanced, IEC 62304 classes A/B/C, IMDRF SaMD categories I–IV. *Applied as R3, and flagged unreviewed.*

**ADD — the forbidden-claims boundary.** The wellness/medical-device line is drawn by **intended use and claims**, not by what the software does. For a coaching app the set of claims the product must **not** make is the artifact keeping it out of device regulation. *Partially applied — R21 records exclusions generically; the sharpened form is not yet in.*

**Three currency errors caught in my own prompt, worth recording:**

- **21 CFR 820.30 no longer exists.** FDA's QMSR final rule (89 FR 7496, effective 2026-02-02) reserved §§ 820.20–820.30 and incorporated ISO 13485 Clause 7.3 by reference. Anything citing 820.30 as current US law is stale.
- FDA's General Wellness guidance was **reissued January 2026**, superseding the 2019 version; its low-risk test is now three questions.
- The Predetermined Change Control Plan guidance was **reissued August 2025**.

______________________________________________________________________

## Not yet applied

Findings from four dimensions read only as headlines. Each is an open item.

### Directly against a current requirement

**Against R25 (archived, not maintained) — for the health workload only.** In US medical-device regulation the requirements artifact is the **opposite** of archived: it is a controlled record under design controls. If any coaching-app feature crosses the wellness boundary, R25 inverts for that workload.

**Against R25 — a named re-run trigger.** If the artifact is archived rather than maintained, something must say when it has gone stale enough to warrant a fresh pass. NIST makes continued re-application an obligation. Our set has no trigger.

**Against R24 (no architecture) — every tradition has an escape hatch and ours does not.** Implementation may be stated **when accompanied by rationale for constraining the design**: INCOSE R31 states the exception inside the rule and makes the rationale mandatory; UK PCR reg 42(13) permits naming a specific make *"on an exceptional basis"*. Our prohibition is stricter than any engineering tradition surveyed.

**Against R25 (open questions exempt) — from two directions.** INCOSE tolerates TBD values **only on the needs side** and refuses to carry them into requirements — a one-way valve, where ours is a permanent exemption at the same level. Procurement is harder still: it has **no notion of a benign open question**, and its governing stance is default-deny — whatever is not written down is not delivered.

**Against R28's ordering.** FAR 10.001(a)(2)(i) mandates market research *"Before developing new requirements documents"* and runs it in **both** directions, letting the verdict rewrite the requirement. Our sequence runs sourcing strictly downstream and lets its verdicts enter only as constraints.

### Additions with no slot in our set

**A precedence rule between requirements.** Our set is flat and all-MUST. Every behavioural specification in the LLM corpus is **layered with an explicit tie-break**, arrived at independently: OpenAI's Model Spec uses five authority levels — Root, System, Developer, User, Guideline — plus conflict resolution. When two requirements collide, ours says nothing.

**Normativity marking.** We mark provenance (R11, R12) but not **which text obliges**. RFC 8174 and BCP 14 exist because `must` and `MUST` were being confused; INCOSE bans `shall` from attribute text outright. Two sources state the failure mode: explanatory text read as an obligation, or an obligation hiding in explanatory text.

**Off-nominal, error and abuse coverage — named as "the single biggest hole".** INCOSE explains why the gap forms: the first pass naturally covers desired behaviour under expected conditions, so off-nominal analysis has to be a deliberate separate act. *Partially applied as R23, from 12207; the INCOSE treatment is fuller.*

**Environmental assumptions, distinct from constraints.** Constraints bind what we may build; environmental assumptions are the claims about the world the requirements silently depend on and that **nobody is obliged to make true**. The FAA handbook gives them their own section.

**Set-level consistency.** R15 governs each requirement in isolation; nothing in our set governs the set as a whole. INCOSE has a set-level characteristic for it; ECSS makes it two `shall`s — internal consistency, and consistency with documents outside the specification.

**Standalone requirements.** A requirement's meaning must not depend on the section heading above it. ECSS makes it a `shall`; INCOSE bans reliance on headings. Directly load-bearing here, because each requirement is extracted and turned into a standalone test.

**Requirement identifiers must be assigned, not positional.** Our numbers are positional. W3C accepted a real cost to keep IDs stable — WCAG 2.2 appends new criteria **out of level order** rather than inserting them, purely so existing numbers do not move. ECSS makes identification a `shall` and asks the identifier to encode type. *Partially applied as R19, which requires stability but not assignment.*

**A bound glossary as a first-class field.** The UK CCS Statement of Requirements template ships a Definitions table immediately before the requirement, pre-filled with the instruction to give each term an unambiguous meaning **for the purposes of this document**.

**Two tiers, structurally.** Every procurement regime splits the artifact into pass/fail requirements a solution must satisfy, and weighted preferences that discriminate among survivors — and refuses to let the mandatory tier stand alone. UK law makes it structural at s.19(2). This is the must/goal split we reached by argument, mandated by statute.

**A per-requirement audit trail.** SI 2024/692 reg 31 requires the assessment summary to carry each criterion's title, relative importance, intended scoring, the score actually determined **for each criterion**, and an explanation. Per requirement, not per document.

**A go/no-go exit after requirements settle.** R2 declines at intake; R10 terminates on the set reading correctly. Neither is a decision about whether to build the thing at all. NIST places exactly that decision at the end of context establishment.

**Worked pass/fail examples as proof of testability**, including the **inapplicable** case. ACT makes this a `MUST` at the rule layer, as a substitute proof where logic alone cannot establish testability.

### Specific to a model-output product

**The meter must be validated before the fit criterion counts.** R14 and R16 require a measurement and a meter but say nothing about whether the meter is trustworthy. When the meter is an LLM judge — which it will be for a coaching app — an uncalibrated meter yields a fit criterion that cannot be relied on.

**Declining must be measured two-sided.** Everywhere declining is a specified requirement in this corpus it is paired with a measurement of **not declining when it should not** — matched contrast sets. R2 specifies the decline condition; nothing measures over-declining.

**Rationale attached to each requirement, distinct from its source.** R11 requires where a requirement came from. Anthropic's published constitution requires something additional: the **reasoning** for the rule, with an operational justification for the practice. Volere has the same field. *Not applied — our card carries Source and Fit, not Rationale.*

**The model provider's usage policy is a binding-constraint source.** For this developer specifically, the acceptable-use policy draws its licence line **through the product**: healthcare, therapy and mental-health uses trigger mandatory human-in-the-loop conditions. R28's sourcing step will miss this entirely if sourcing means libraries and prior art.

______________________________________________________________________

## Method and limits

Six corpora, one isolated agent each, with adversarial verification on the load-bearing ADD and RECALIBRATE verdicts. Agents were given the twenty-five requirements flat and **were not told where the gaps were believed to be** — a correction from earlier sweeps in this session, which primed agents by naming the expected gaps in the guard block.

**Read in full and applied:** regulated health software; product discovery.
**Read as headlines only:** LLM behaviour specifications; systems and safety engineering; procurement; testable-at-scale formats. Their findings above are transcribed from verdict summaries, **not from the underlying sources**, and none has been checked against a primary. Treat every item under "Not yet applied" as a lead, not a finding.
