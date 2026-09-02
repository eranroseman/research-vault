# Requirements: writing-requirements (the pre-spec phase)

> **For agentic workers:** REQUIRED SUB-SKILL: `writing-specs`. This document is the input to the design phase, not a design.
>
> **Status:** draft, 2026-09-01, revised the same day after review. **Not confirmed** — the gate this document specifies has not been run on this document. Identifiers are never changed and never reused, which is why splitting R4 and R9 produced R30 and R31 rather than renumbering.
>
> **Delete when** `writing-requirements` ships and its skill body carries these requirements, or when the design is abandoned. This document is scaffolding, not a record: git history holds it after deletion. Precedent — `553ae6f`, "delete 14 merged/abandoned superpowers plan files". A never-maintained file sitting at a stable path is the stale record that deletion exists to prevent.
>
> **Sequencing, ruled 2026-09-01:** build now, not after `writing-specs`. `writing-requirements` is written here, drawing text from four skills rather than vendored from any one — so it never merges upstream, was never a drift surface, and waiting for `writing-specs` buys nothing. The two are not siblings and are not required to match; each carries what its own altitude needs. **The R27 gate is lifted, 2026-09-01** — all six corpora are read and applied; `docs/research/2026-09-01-r27-completion.md` carries the result. Nothing now blocks building.
>
> **Durable home** is the `software-development` repository, which does not exist yet. #59 owes its **structure decision**, not the repository — its own body puts building it out of scope. This tree is the working home while the design dossier lives here, not the destination.

## Problem

I build software with AI agents, alone, across three workloads: my own tooling, a research vault, and HITL health-and-wellness coaching apps. The process I want runs from "I have this idea" to working software.

The process I have starts one step too late. `writing-specs` takes an idea and produces a technical design; it assumes I already know the what. So the what and why never get written down — it asks me for purpose, constraints and success criteria every time, steers the design with them, and records none of them.

The cost lands on my attention. An agent starts work carrying assumptions I never gave it and it never declared, and I find them by interrogating it three rounds later. Interviews are not the cost — I will take an agent interviewing me all day if that gets the job right. Interrogation is the cost.

The absence is not hypothetical. Five artifacts compensate for it somewhere else — four named here and `interview-me` found later by the sourcing screen. Three are in my roster: `brainstorming` asks the questions in a conversation that discards the answers; `rethink-audit` carries it as rung one of an audit method; this repo's foundation spec puts it in §1 of the design document. The fourth, mattpocock's `to-spec`, is neither installed nor adopted here — it puts Problem Statement and User Stories inside a spec template, and its author documents the resulting deformation.

A survey of ten agent coding frameworks found none with a phase before design. **That survey was run in conversation and never written up** — the claim has no evidence trail, unlike the prior art, competitive analysis and sourcing screen linked below.

## Solution

A phase before `writing-specs` that turns a need into a written, verified statement of what and why, and nothing about how.

`brainstorming` is how-brainstorming. This is what-brainstorming: the same collaborative dialogue one level up, named for its output the way `writing-specs` is.

It runs as a loop, not a document generator — interview for the why and what, write the requirements, verify we understood the same thing, repeat until converged. It ends when I say the restated set is right.

## Assumptions

Claims about the world this phase depends on and that **nobody is obliged to make true** — distinct from constraints, which bind what may be built. The distinction and the separate section are the FAA handbook's.

- **One person holds the need, the decision and the cost.** This is why most of the field's apparatus does not transfer, and it is the assumption most likely to become wrong later. It was previously filed as an out-of-scope item ("aligning multiple stakeholders"), which read as a decision this phase made; it is not one, and 12207 6.4.2 outcome (g) contemplates multiple stakeholders throughout.

## Prior art

Read before the requirements were written, and the source of most of them. Full reading, including the traditions that declined to supply anything: `docs/research/2026-09-01-requirements-artifact-prior-art.md`.

**The headline finding is a rediscovery.** What the older traditions do have, they had early: the Volere shell carried Description, Rationale, Originator and Fit Criterion per requirement in the 1990s, which makes the modern six-field convergence a lossy rediscovery rather than a new result.

| Source                                      | What it gave                                                                                                                                                                                | Requirements                           |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| ISO/IEC/IEEE 29148:2018                     | 5.2.5 characteristics; 5.2.6 TBx; 5.2.7 forbidden terms and the no-how rule; 5.2.8 identifiers                                                                                              | R15, R18, R19, R24, R25, R28           |
| ISO/IEC/IEEE 12207:2017                     | 6.3 rigour scales with risk; 6.4.2.2(g) agreement as an outcome; 6.4.2.3(c.1) abuse and failure; (d.1) constraint sources; (d.2) critical quality characteristics                           | R3, R10, R22, R23                      |
| ECSS-E-ST-10-06C                            | 5.2 the two-baseline process and the low-heritage gate; 7.2.3d consistency; 7.2.7a informative clauses carry no requirement; 8.2.8a self-contained; Annex A the normative table of contents | R26, R27, R29, R31, R35, R37, R38, R40 |
| FAR Parts 10, 11, 16                        | 10.001(a)(2)(i) research before requirements; 10.002(a) the entry condition; 10.002(c) re-evaluate the need; 11.105 "or equivalent"; 16.603-2(c) a deadline on the unresolved               | R1, R24, R25, R26, R28                 |
| FAA REMH DOT/FAA/AR-08/32                   | §2.4 environmental assumptions; §2.8.4 one ideal value per variable; §2.11.7 capture rationale as you go                                                                                    | R8, R36, R37                           |
| INCOSE GtWR V3.1                            | R25 headings; R29 classify as a completeness device; the five set-level characteristics                                                                                                     | R3, R31, R35                           |
| Volere requirements shell                   | Description, Originator, Fit Criterion                                                                                                                                                      | R11, R14                               |
| Gilb, *Competitive Engineering*             | Scale and Meter; `Fail` (a constraint) versus `Goal` (a target)                                                                                                                             | R16, R17                               |
| Fitzpatrick, *The Mom Test*                 | Specifics in the past, not generics or opinions; exact quotes wrapped as verbatim                                                                                                           | R6, R13                                |
| Willis (1999 and 2012); Pew Research Center | List all reasonable possibilities rather than suggesting one                                                                                                                                | R5                                     |
| Beyer and Holtzblatt, *Contextual Design*   | The Interpretation principle — an interpretation is validated by sharing it                                                                                                                 | R9                                     |
| NIST AI 100-1                               | MAP 1.1 intended purpose and setting; go/no-go as a named process outcome                                                                                                                   | R3, R32                                |
| IMDRF SaMD N10, N12, N41                    | Medical purpose as the gate; the I–IV matrix; categorization relies on the definition statement; rigour commensurate with risk                                                              | R3                                     |
| IEEE adoption of ISO/IEC 15026-3            | Risk analysis before the first integrity-level assignment                                                                                                                                   | R3                                     |
| OpenAI Model Spec 2026-08-18                | Overridable authority levels; name the missing artifact rather than supplying it                                                                                                            | R33, R39                               |
| Anthropic Usage Policy                      | High-Risk use cases; human-in-the-loop; the wellness carve-out                                                                                                                              | R22                                    |
| PCR 2015 reg 42(13)                         | Naming a specific make "on an exceptional basis", with "or equivalent"                                                                                                                      | R24                                    |

None of these is a sourcing decision. They generated requirements; they are not components and nothing is bought from them. The sourcing section below holds only skills and skill components.

**One requirement has no anchor here.** The phase's own success criterion is stated by no tradition surveyed — named rather than stretched onto a near-miss.

## Competitive analysis

Ran **after** the requirements were drafted, against six corpora, and edited the set. It is presented **before** them because the set shown below is the post-update one: several requirements exist only because this pass found them, so reading the requirements first would leave those unexplained. Full verdicts: `docs/research/2026-09-01-pre-spec-competitive-analysis.md`.

**What it changed.** The largest correction was to the interview loop: the guess-attached question is backward-looking in both traditions that use it, and attaching a forward guess to an open question is a mutation with measured harm — acquiescence bias, worse with an interviewer present. Willis's rule — list all reasonable possibilities rather than suggesting one — replaced it as R5. (An earlier draft called this "multi-possibility probing"; that label is **not** in either Willis guide and is withdrawn.) Anchoring elicitation in specific past events entered as R6, the single most-agreed rule in the discovery corpus. R9 was recalibrated because confirmation is continuous in both traditions that use it, not concentrated into one terminal restatement. Verbatim-marked-as-verbatim entered as R13, and a declared risk tier as R3. R7's question-cap survived a null result in its favour — nobody caps question count.

**Two disagreements were recorded rather than resolved.** Fitzpatrick argues verbal assent is precisely the data type that must not terminate elicitation; 12207 6.4.2.2(g) makes stakeholder agreement a process outcome. R10 takes the standards position with the dissent noted.

**Status: complete.** Two of six corpora were read in full in the first pass. The remaining four — LLM behaviour specifications, systems and safety engineering, procurement, and testable-at-scale formats — were read properly on 2026-09-01 and are recorded in `docs/research/2026-09-01-r27-completion.md`. That pass produced 74 findings, sent 16 to adversarial verifiers, and **9 survived**: five new requirements (R35–R39) and four recalibrations (R22, R24, R25, R28). R21 was reframed in the same pass but on the author's ruling rather than on R27's evidence, which corroborated it without being the authority.

**Two things it did not support.** R24's missing escape hatch was confirmed, but not on the grounds first recorded — the three procurement regimes cited are not independent, all descending from WTO GPA Article X. And the predicted two-tier gap — that the sourcing screen is mandatory-only where procurement forbids a mandatory tier standing alone — **is not established**. The corpus's decision rule for the split was verified and refuted, and the surviving finding rests on a goals section this document does not have, asserted falsely in my own guard block. Nothing from the testable-at-scale corpus is applied: all four of its verified findings broke on generalisation or transfer despite exact quotes.

## Requirements

**Retired numbers: R3, R10, R16, R17.** All dropped on 2026-09-02 under the test *"if dropped, does it hurt functionality or remove needless ceremony?"* — none had a consumer. R16's measurement-method clause survives inside R14. R34 is now issued; R41 is a split from R22. Identifiers are never reused (R19), so the gaps are deliberate.

Source vocabulary, defined by **origin** rather than by confirmation status: `elicited` — stated directly, quoted where short. `inferred` — derived from what was stated. `assumed` — brought from the agent's general knowledge rather than from anything said. Otherwise a named document. Any of the three may be confirmed or not; confirmation is tracked separately, because defining a class by confirmation status leaves agent-supplied-and-confirmed material with no label — which is what R12's three classes and R23 both need.

### Skill behaviour

**R1** — Accepts a need arriving unframed in conversation.
*Fit:* a bare sentence with no user, no success criterion and no constraint produces a first turn, not an error.
*Source:* FAR 10.002(a), FAC 2026-01 — "Acquisitions begin with a description of the Government's needs stated in terms sufficient to allow conduct of market research." A rough description is the legitimate entry state, not a defect. Verified locally 2026-09-01. Previously `elicited` — "the usual route is chat → spec → plan" — which is still the origin, now with a primary behind it.

**R2** — Declines when no real question remains, the work is small, or the approach is already chosen.
*Fit:* the run checks three conditions — a real question remains open, the work exceeds a quick change, the approach is still undecided. Any condition that fails ends the run in one sentence naming how to invoke the skill deliberately.
*Source:* `neuroarxiv` and `adhd` pre-flight gates, both with an explicit-invocation bypass.

**R4** — Asks questions in dependency order.
*Fit:* no question is asked whose answer hinges on another still open in the same round.
*Source:* `mattpocock/skills` commit `a4b2009a` — "Same 13 questions land in ~3 rounds instead of 13."

**R30** — Asks mutually independent questions in one round.
*Fit:* two questions, neither depending on the other's answer, arrive in the same round.
*Source:* as R4. Split out because the two were joined by a conjunction and only the first was tested — the sourcing screen failed `interview-me` on the second half while R4's written fit would have passed it.

**R5** — Offers the plausible alternatives, never a single guess, when it proposes an answer before the user gives one.
*Fit:* every question that proposes answers offers two or more, and marks none of them as expected.
*Source:* Willis, *Cognitive Interviewing: A "How To" Guide* (1999, Research Triangle Institute / ASA short course) **and** *Cognitive Interviewing Training Guide* (2012), **both read directly 2026-09-01**, carrying the passage **identically thirteen years apart** — "rather than suggesting to the subject one possibility ('Did you think the question was asking just about physicians?'), it is preferable to list all reasonable possibilities… probes should be characterized by unbiased phrasing". **Correction:** the labels "single-possibility" and "multi-possibility probing" appear **nowhere** in either guide, nor in a published review of the 2005 book. Searched in three documents, zero hits. They were reported as quotation and are not. The substance is verbatim, the terminology is not from this source. Pew Research Center, *Writing Survey Questions* (methods section, `pewresearch.org/writing-survey-questions/`), **read directly 2026-09-01** — "This is sometimes called an 'acquiescence bias'… This behavior is even more pronounced **when there's an interviewer present**, rather than when the survey is self-administered. **A better practice is to offer respondents a choice between alternative statements.**" Pew independently supplies the *remedy*, not merely the harm, so R5 has two legs that converge.

**R6** — Anchors questions about the problem in specific past events, not in opinions, generalities or predictions.
*Fit:* every question about the need, its cost and the current workaround asks what happened. Only questions about the wanted outcome ask about the future, and the artifact records their answers as goals rather than as evidence.
*Source:* Fitzpatrick, *The Mom Test*, **read directly 2026-09-01**, rule 2 of three: "Talk about their life instead of your idea. **Ask about specifics in the past instead of generics or opinions about the future.** Talk less and listen more." Verbatim, and the requirement is a restatement of it. The competitive analysis additionally claimed convergence across "three independent primaries"; **two were never named and remain unrecovered**, so the convergence claim stays unverified even though the requirement no longer depends on it.

**R7** — Stops questioning on convergence, never on a count.
*Fit:* no number anywhere in the skill limits how many questions it asks or how many open questions (R25) the artifact holds.
*Source:* a **null result** from the competitive-analysis pass, which is evidence rather than an absence of it: no practice surveyed caps question count, and every one caps something adjacent instead — learning goals per person-type, session length, question density. Searching 29148 and 12207 for any cap on elicitation effort returned nothing, consistent with that. Competitive-analysis derived, not prior art; no prior art exists to derive it from. The author's position — "I prefer agents interviewing me all day long if that is what is needed to get the job right" — is the origin.
*Note:* drove no rejection in the sourcing screen except jointly with R1. May be describing the field rather than screening it.

**R8** — Writes each requirement in the round its answer settles.
*Fit:* at the end of every round, the artifact holds a requirement for each answer that round settled. A run that reaches the terminal restate with requirements written after the last question fails.
*Source:* FAA REMH DOT/FAA/AR-08/32 §2.11.7, verified locally 2026-09-01 — "Rationale should be collected along with the development of the requirement… This ensures that the justification is captured by the author while he or she is thinking about it… it is much simpler to record the rationale when the latency was being computed than to try to re-engineer the reasoning later." The reason given is the author's attention, which is this requirement's reason too. Origin: `elicited` — "interview user for why and what, write requirement, verify, repeat until done."

**R9** — Restates each requirement to me when it is written, and records whether I confirmed it.
*Fit:* every requirement in the artifact carries a confirmation status. A requirement I have not confirmed is marked as such and reaches the terminal restate (R31) still marked.
*Source:* Beyer and Holtzblatt, *Contextual Design*, the **Interpretation** principle, **read directly 2026-09-01** — "If the data that matters is the interpretation, we must have a way to ensure it is correct, and we can only do that by **sharing it with the customer**. We fail in the entire purpose of working with customers if we do not share and validate our interpretations of their work." Sharing is continuous and per-interpretation, not terminal, which is what R9 requires and R31 completes. Qualitative research's *member checking* is the second tradition, still not read directly. The rendering into a per-requirement obligation remains mine.

**R31** — Restates the accumulated set before terminating.
*Fit:* the final restate covers every requirement written, not only those settled last.
*Source:* ECSS-E-ST-10-06C 5.2, verified locally 2026-09-01 — "The customer assesses the entire set of technical requirements for correctness, consistency and suitability for the intended use." The task appears **twice**, as F1.3 and again as F1.9, each immediately before a release task, so a whole-set assessment before terminating is a distinct process step rather than a by-product of per-item confirmation. INCOSE GtWR V3.1 places five characteristics at set level for the same reason — C10 Complete, C11 Consistent, C12 Feasible, C13 Comprehensible, C14 Able to be Validated — properties that cannot be checked one requirement at a time. Split from R9 because continuous confirmation and a terminal restate are two obligations and a skill could satisfy either alone; that split is now backed rather than asserted.

**R37** — Before the terminal restate (R31), checks the accumulated requirements as a set.
*Fit:* the sweep reports four results. (1) Conflicts: for each pair sharing a subject, whether their conditions can hold at once, and where they can, that their outcomes agree. (2) Duplicates: no obligation appears twice. (3) Terminology: each term carries one meaning throughout, and every term a requirement refers to is defined by a requirement in the set. (4) Non-singular statements: each requirement states one obligation, which R15 governs per item and only a whole-set pass reliably catches. A collision the sweep finds is resolved, or recorded under R25, before the restate.
*Source:* R27, survived verification. ECSS-E-ST-10-06C 7.2.3d — "The technical requirements shall be consistent (e.g. not in conflict with the other requirements within the specification)" — with FAA REMH 2.8.4 giving the operable form, "only one ideal value is assigned to each controlled variable and each internal variable for every possible system state", and INCOSE C11 adding terminology homogeneity. Every rule in the set to this point governs a requirement in isolation; nothing governed the set. The non-singular sweep is ISO/IEC/IEEE 24748-2:2024's — "The resulting set of technical requirements should be checked for non-singular requirements containing multiple parts, which should then be decomposed into individual (singular) requirements" — added because this document hit that defect **twice**: R4 and R9 were each a conjunction with an untested half, split into R30 and R31 only after the sourcing screen caught one by accident. A standard treats it as routine.

**R34** — Runs on Claude Code and Codex.
*Fit:* the skill body invokes only mechanisms both harnesses provide, and a fresh install on each harness produces one complete artifact from one run.
*Source:* the author's ruling of 2026-09-02, promoting it from a constraint on the 29148 3.1.7 test — the harnesses are pre-existing, but supporting both could have been decided otherwise, so it is a requirement. The failure it prevents has already occurred here: #56 records Codex dropping a tracked symlink, so 8,873 bytes of plugin-level `AGENTS.md` guidance arrived silently absent. "From a fresh install" is what catches packaging failures that a body-only check misses.

### Artifact content

**R11** — Each requirement names where it came from.
*Fit:* every requirement carries an origin a reader can check — a passage of the transcript or a named document.
*Source:* Volere requirements shell, `Originator`; 12207:2017 6.4.2.2(i).

**R12** — Distinguishes what I said, what the agent inferred from what I said, and what the agent brought from general knowledge.
*Fit:* for each requirement, a reader can say which of the three it is.
*Source:* `matter-intake-scoping`'s four-level provenance scheme. 12207 treats implicit needs from domain knowledge as a legitimate input, so this marks rather than forbids.

**R13** — Marks quoted material as verbatim, distinct from paraphrase.
*Fit:* quotation marks enclose only words the source used, whether the source is me or a document, and a reader can tell a quotation from the agent's summary of it.
*Source:* Fitzpatrick, *The Mom Test*, **read directly 2026-09-01** — "When possible, **write down exact quotes. Wrap them in quotation marks so you know it's verbatim.** … Other times the exact quote isn't relevant and you just write down the big idea." That is this requirement, stated as practice. His reason: "**notes make it harder to lie to yourself**." **Correction:** the phrase previously attributed to him in quotation marks — "the artifact's job is to make self-deception harder" — **does not appear in the book**; "self-deception" occurs zero times. It was an agent's paraphrase presented as a quotation. The idea survives in his own words; the quotation is withdrawn.

**R14** — Each requirement carries a fit criterion: one measurement that tests whether a solution matches it.
*Fit:* each requirement carries exactly one measurement, naming what is measured and how it is measured, that a reader can run against a candidate solution to get a pass or a fail. Per requirement, never per goal and never per document.
*Source:* Volere requirements shell — "A measurement of the requirement such that it is possible to test if the solution matches the original requirement." The "how it is measured" clause absorbs the dropped R16, whose source was Gilb, *Competitive Engineering* (2005): "**Meter:** A practical method for measuring and testing a scalar attribute level, on a defined Scale."

**R15** — Each requirement states a single capability, characteristic, constraint or quality factor.
*Fit:* no conjunction joins two.
*Source:* ISO/IEC/IEEE 29148:2018 5.2.5.

**R18** — Each requirement avoids terms whose meaning a reader must guess.
*Fit:* no requirement contains a superlative, a comparative, a subjective adjective, an ambiguous adverb or pronoun, a totality term (`all`, `always`, `never`), a loophole (`where feasible`, `as appropriate`, `if practical`), an open-ended term (`etc.`, `and so on`), or a reference to a document, section or term the artifact does not name.
*Source:* ISO/IEC/IEEE 29148:2018 5.2.7 — "Vague and general terms shall be avoided."

**R19** — Requirement identifiers are never changed and never reused.
*Fit:* an R-number cited in a later round means what it meant in the first.
*Source:* ISO/IEC/IEEE 29148:2018 5.2.8.2.

**R20** — Records the problem and the intended outcome as I experience them.
*Fit:* each names what I do today and what I would do instead — an experience, not a system property and not a product gap.
*Source:* `to-spec`'s first half; `helm-brief`'s test — "Must describe a user experience, not a product gap."

**R21** — Records the boundary of the need: what falls inside it and what falls outside.
*Fit:* a reader can place a candidate feature on one side or the other without asking. A list of things not being built does **not** satisfy it.
*Source:* `interview-me`, `shape-spec` and `helm-brief` independently. Reframed from "records what is excluded" on 2026-09-01, on the author's ruling that a requirements document does not contain a list of non-goals — the four items removed from this document's own Out of scope section were definitional, not chosen. R27 corroborates from two corpora, which frame the item as a boundary rather than as an exclusion list; that finding was not itself verified, so the ruling is the authority and the corpora are support.

**R22** — Records each constraint that binds this need.
*Fit:* each constraint is falsifiable and passes 29148 3.1.7 — an *"externally imposed limitation… imposed on the solution by force or compulsion"* — so anything that could have been decided otherwise is a requirement, not a constraint.
*Source:* 12207:2017 6.4.2.3(d.1) — constraints include "required use of defined enabling, legacy, or interfacing systems" and "unavoidable consequences of existing agreements", which is why an already-binding sourcing decision is a constraint by definition and needs no clause of its own.

**R41** — Where the product calls a model, records the acceptable-use conditions the provider's policy imposes on this need.
*Fit:* the artifact names the use-case class this need falls in, quotes the conditions that class triggers, and carries each as a constraint under R22 — or records that no class applies, and why.
*Source:* R27, survived verification. Anthropic's Usage Policy requires that for High-Risk use cases "a qualified professional in that field must review the content or decision prior to dissemination or finalization", classes "therapy, mental health" as High-Risk, and carves out "advice on sleep, stress, nutrition, exercise" — a boundary running through the coaching-app workload. Split from R22 on 2026-09-02: one statement carried two obligations, which R15 forbids and R37 sweeps for.

**R23** — Generates requirements from abuse and failure scenarios, not only from stated needs.
*Fit:* the artifact contains at least one requirement nobody asked for.
*Source:* 12207:2017 6.4.2.3(c.1) — "Abuse and failure scenarios highlight the need for additional functional requirements."

**R24** — States what the need requires, not how to build it.
*Fit:* nothing in the requirement list changes if the implementation approach changes. Sourcing verdicts live in their own section under R28 and are exempt. Where no functional or performance statement can make a requirement understood, that requirement names the property actually required and marks any named product as an example, not a choice.
*Source:* 29148:2018 5.2.7 — "Requirements should state 'what' is needed, not 'how'." A `should`, with an acknowledged exception at lower decomposition levels. The exception's form is R27's, survived verification: PCR 2015 reg 42(13) permits naming a specific make "on an exceptional basis, where a sufficiently precise and intelligible description… is not possible, in which case the reference shall be accompanied by the words 'or equivalent'". Where the exception is used here, the requirement names the property actually required and marks the named thing as an example, not a choice. One sub-claim was struck in verification: PCR, the Procurement Act 2023 and FAR Part 11 are **not** three independent regimes — all descend from WTO GPA Article X. The independent second leg is INCOSE and ECSS, which state the same exception inside the rule.

**R25** — Records open questions; an open question does not stop the set from being confirmed.
*Fit:* each open question names the downstream point that must resolve it, and a reader proceeds past every open question without contacting me.
*Source:* 29148:2018 5.2.6 permits TBx during evolution — "Resolution of the TBx designations may be iterative and there is an acceptable timeframe for TBx items" — and forbids them at completion. The resolution-point half is R27's, survived verification: FAR 16.603-2(c) lets a binding instrument carry an unresolved item only against a deadline — "definitization of the contract within 180 days… or before completion of 40 percent of the work to be performed, whichever occurs first". The exemption holds because this artifact is never the completed set: it is an input to a design phase that resolves the open items, and it is archived rather than contracted.

**R33** — In a non-interactive context, names the questions it would have asked and stops, rather than answering them itself.
*Fit:* a run with no user produces a question list and no requirements.
*Source:* OpenAI Model Spec 2026-08-18, verified locally 2026-09-01. Guideline: "Consider uncertainty, state assumptions, and ask clarifying questions when appropriate." Its worked example "Ambiguous request where a missing artifact is likely" makes the compliant response name what is missing — "I think you might have forgotten to paste or upload the text you want me to revise" — and makes proceeding by supplying the content yourself the violation. **Lowest usable rung**: a vendor's specification of its own models, not standards-body consensus. Origin: `elicited`, as a scope note; numbered here because it is behaviour, not scope. The subagent run of 2026-09-01 is the worked example — and it detected the absent user because it was told, not because anything in this design would have.

**R32** — Records my verdict on the terminal restate (R31): confirmed, or not confirmed.
*Fit:* a cold session opening the file names the verdict without asking me, and distinguishes a confirmed set from an abandoned draft. Open questions recorded under R25 do not make a set unconfirmed.
*Source:* NIST AI 100-1, verified locally 2026-09-01: an "explicit process for making go/no-go system commissioning and deployment decisions" is a named benefit the framework exists to produce, and it is placed after context is established and before building — this requirement's exact position. Previously `inferred` from R8, R31 and R29 interacting, which remains the derivation of its necessity here: R8 leaves a partial artifact on disk mid-interview, R29 promises cold-session consumption at a stable path, and R31 produces a verdict nothing else records. R8 guarantees a partial artifact exists on disk mid-interview; R29 promises cold-session consumption at a stable path; R31's terminal restate produces a verdict that nothing else records. Without this, `writing-specs` cannot distinguish a set I confirmed from one I walked away from.

**R35** — Each requirement is complete on its own: its meaning does not depend on its section heading, on neighbouring requirements, or on surrounding prose.
*Fit:* lift any single requirement out of the artifact, with no other text, and a reader who has not seen the artifact can say what is required and what would violate it — without asking what "it" or "the system" refers to.
*Source:* R27, survived verification. ECSS-E-ST-10-06C 8.2.8a — "A technical requirement shall be self-contained", noting it "does not require additional data or explanation to express the need" — and INCOSE GtWR V3.1 R25, "Avoid relying on headings to support explanation or understanding of the requirement." Load-bearing here because R14 turns each requirement into a standalone test.

**R36** — Records each assumption the requirements depend on and that no party is obliged to make true, in a section separate from constraints.
*Fit:* for each assumption, the artifact names who or what would have to change to make it false, and states that nobody on this project controls that. A statement failing that test is a constraint under R22.
*Source:* R27, survived verification. FAA REMH DOT/FAA/AR-08/32 §2.4 — "These are actually requirements levied by the system on its environment… Failure to identify the environmental assumptions and the subsequent misuse of the system is a common cause of system failure." This document's own Assumptions section was added on 2026-09-01 from the competitive analysis's headline; this is the primary behind it, read directly.

**R38** — Confines obligations to requirement statements.
*Fit:* no sentence outside a requirement statement carries `must`, `shall` or `will`. Any obligation found in explanatory text is promoted to a numbered requirement before the terminal restate under R31.
*Source:* R27, survived verification. ECSS-E-ST-10-06C 7.2.7a — "If a clause is stated to be informative or descriptive, then this clause shall not contain any requirement or recommendation" — with 8.3.2 fixing the verbal forms. *The agent's proposed wording also assigned `should` to goals; dropped, because there is no goals section and that clause came from a premise this project's own guard block supplied falsely. Recorded in the R27 note.*

**R39** — Where a model generates the product's user-facing output, records the behaviour required of the model in each sensitive interaction the product's flows can reach.
*Fit:* for each flow reaching a use-case class recorded under R41, the artifact states what the model must do and what it must refuse. A product with such a flow and no such statement fails this requirement. Does not apply where no model output reaches a third party, which exempts the research vault and personal tooling.
*Source:* R27, survived verification. OpenAI Model Spec 2026-08-18 tags "Provide information without giving regulated advice" **Developer** and "Support users in mental health discussions" **User** — both below Root, so a developer may override them and silence accepts them. **What transfers is the structure**, not the provision list: published defaults exist, are overridable, and bind by silence. The list is OpenAI's and does not govern a product running on Claude; the binding instrument there is the Usage Policy, under R22.

**R40** — The artifact's sections follow the order of the phases that produced them, and each carries or links the evidence that phase produced.
*Ceremony test, 2026-09-02: DROP — and not applied.* Nothing in the set reads R40, which is the shape that retired R3. **But you instructed this structure directly** ("the docs sections should follow the process phases to reflect the work that was done"), so the test and an explicit ruling disagree and the ruling is yours to make. Held pending that.
*Fit:* a reader can name which phase produced each section and reach that phase's evidence from inside it, without an index. A section for a phase that never ran does not appear. Where an output depends on a phase that ran after it — the requirement set is the post-competitive-analysis one — presentation order differs from run order and the section says so.
*Source:* ECSS-E-ST-10-06C Annex A, **verified locally 2026-09-01** — a normative Document Requirements Definition mandating the table of contents, section by section, which is the same claim as "sections follow the phases" made by a standards body. No longer an unverified lead. The author's rulings of 2026-09-01 remain the origin: "the docs sections should follow the process phases to reflect the work that was done", and that prior art and competitive analysis precede the requirements "as some of the reqs are derived from the comp analysis".

### Pipeline

These three are requirements on the **phase**, not on any single skill. Every candidate failed all three — which measures the granularity of the screen, not a gap in the field. A skill does not contain three sub-steps that are themselves skills; a pipeline composes them. They are satisfied by the composition and are not screening criteria for any component of it.

**Delivery, ruled 2026-09-01: one skill with three internally-gated phases**, each dispatching an isolated subagent. Three named sub-skills would put three descriptions with exactly one caller each into the router's match pool — the same failure `grilling`'s description suppression was fighting. Delegating to the installed `research` skill fails R26's fit, which requires patterns to arrive already shaped as requirements rather than as candidates to weigh. The one real cost — phases not independently re-runnable — is met by an optional entry argument naming a phase, so re-running sourcing alone does not mean re-entering the loop.

**R26** — Searches prior art before writing the first requirement.
*Fit:* the phase begins once the need is described well enough to search on, and skips the search only where the need repeats work this project has already built. What the search returns enters the artifact as requirements carrying their sources; a list of patterns to weigh later fails.
*Source:* two primaries, verified locally 2026-09-01. FAR 10.001(a)(2)(i) mandates the ordering in the imperative — agencies shall conduct market research "Before developing new requirements documents" — and FAR 10.002(a) supplies the gate's entry condition, a need described well enough to research against: enough to search on, not enough to specify. ECSS-E-ST-10-06C 5.2 states the gate's *exit* condition — the concept-exploration step "is needed in phase 0 for space projects with **low heritage**", so high heritage skips it. Origin: `elicited`. The cost of skipping it was paid in this session.

**R27** — Runs a competitive-analysis step that edits the requirement set before the confirm gate.
*Fit:* its output is edits to requirements — added, recalibrated, dropped, confirmed — not verdicts on competitors.
*Source:* ECSS-E-ST-10-06C 5.2, verified locally 2026-09-01 — "The second step consists of the exploration among the different possible concepts… This version is progressively drafted from the preliminary TS and takes into account the induced constraints from the possible concepts." A concept step that **amends** an earlier requirement baseline rather than replacing it is this standard's normative two-baseline structure, which is the ordering chosen here. Origin: `elicited` — "how my requirements compare to other solutions."

**R28** — Runs the sourcing screen after the requirement set settles.
*Fit:* a reader can tell which ran first. Verdicts land in a section of their own, never as requirements, and name components rather than whole skills. Where a verdict finds nothing available, the named requirement re-opens and carries either a restatement or a recorded decision to build it bespoke, before the terminal restate.
*Source:* 29148:2018 5.2.5 NOTE 1 names "a system that can be bought rather than made" as an inappropriate requirement; Volere places Off-the-Shelf Solutions at section 19, separate from Functional Requirements at 9. The re-opening half is R27's, survived verification: FAR 10.002(c) runs market research **both** ways — "agencies shall reevaluate the need… and determine whether the need can be restated to permit commercial products… to satisfy the agency's needs." An earlier version of this requirement was a one-way valve, which the primary is not. The component-level clause is the author's ruling of 2026-09-01.

### Integration

**R29** — Output lands at a stable path.
*Fit:* a cold session hands the artifact to `writing-specs` without asking where it is, on either harness.
*Source:* ECSS-E-ST-10-06C Annex A (normative) A.2.1 \<1>, verified locally 2026-09-01 — "The TS shall contain a description of the purpose, objective, content and the reason prompting its preparation." The header carries four things there and one here. **The gap is "the reason prompting its preparation"**, which is precisely what an artifact archived and never maintained loses first. Previously the house convention alone, specified verbatim in `writing-plans`' plan header; that remains the format, now with a standard behind the obligation.
*Note:* every candidate failed it, so it screened nothing — the same shape as R26–R28. An obligation on what we build, not a discriminator among what we might take.

## Constraints

**Test applied**, ISO/IEC/IEEE 29148:2018 3.1.7: a constraint is an *"externally imposed limitation… imposed on the solution by force or compulsion"*. Could it have been decided otherwise? If yes it is a requirement, not a constraint.

- **Archived on handoff, never maintained — inherited, not chosen here.** This is how the whole superpowers workflow operates: specs and plans are archived once implemented, and this artifact sits in the same pipeline. Drift from the product is expected. Two competitive-analysis findings push against it — a controlled-record obligation under design controls if a coaching-app feature crosses the wellness boundary, and the absence of any named re-run trigger. Neither is answerable inside this phase; both are about the pipeline. **Neither has a tracker home yet** — they sit in the competitive-analysis note, which is temporary, and which ticket takes them (#60, #62 or #63 territory) is unresolved. Carried as a leftover for the #81 post, not silently absorbed.
- `writing-specs` is the only consumer. (An earlier version added "and it is not modified by this phase", which is definitional rather than imposed.)
- **Enumerability is a pipeline obligation, and it is not discharged here.** `writing-plans` never reads this artifact — its Self-Review walks the *spec* against the *plan*: "Can you point to a task that implements it? List any gaps." So each requirement must survive into the spec in a form that check can walk. **Nothing in this phase can guarantee that**, because the guarantee belongs to `writing-specs`' own design, which #60 and #62 own. Filed there as an obligation, not left here as an aside. (An earlier version claimed `writing-plans` consumes this artifact directly; it does not.)
- MIT and Apache-2.0 attribution is owed wherever text is taken substantially, regardless of how the maintenance relationship is described. The licence is the constraint — 29148's own example is *"laws of a particular country"* — and carrying the attribution is a requirement derived from it, currently unnumbered.

## Sourcing decisions

> **Provisional, 2026-09-02. Every verdict below is suspended pending a re-run.** Sourcing was screened against the requirement set as it stood on 2026-09-01. That set is changing: R3 and R10 are dropped, R34 is issued, and every remaining requirement is being tested for whether it earns its place. A screen is only as good as the requirements it screened against, so these verdicts do not carry.
>
> One is already void rather than merely stale. `interview-me` holds an Adapt row for "the explicit-yes gate with its enumerated false yeses" — a gate that R10 defined and that no longer exists. The whole section is re-run once the requirements are final.

Sourcing sits in this phase because `writing-specs` cannot hold it — its approach comparison is architectural alternatives inside your own tree, not build-or-buy. **Trigger to move: `writing-specs` gains build-or-buy comparison.**

Full screen, method and per-candidate failures: `docs/research/2026-09-01-pre-spec-sourcing-screen.md`.

**Screen result, 2026-09-01.** Twelve candidates screened pass/fail against the twenty-nine requirements that existed at the time, one isolated agent each, every result adversarially verified. **R30, R31 and R32 post-date the screen and no candidate has been tested against them.** R30 exists to preserve a measured failure: the screen failed `interview-me` on the batching half of the old R4, and the narrowed R4's fit would no longer record it. No candidate ever passed R4 — it appears in no pass column — so nothing was flipped by the split. Claimed passes ran three to eight; after verification **nothing exceeds three of twenty-nine**. `write-spec` is the only candidate passing **R14** after verification, which is the useful part of that result: it establishes the per-requirement fit criterion is achievable in a skill body, not just in a standard. It earns no adapt row. Its acceptance-criteria section is 29148 5.2.7 (forbidden terms), 29148 5.2.5 (independently testable), 12207 (negative and edge cases), Volere (the criterion itself) and BDD's Given/When/Then, each already sourced here from its origin rather than from an intermediary. What is genuinely its own is the P0/P1/P2 three-tier priority scheme, which this set declines.

That measurement closes the top three treatments — **install a plugin as-is**, **fork it and keep merging**, **copy it frozen** — since each takes something failing at least twenty-six musts.

What remains is **copy plus a delta**, **author to someone else's design and credit it**, or **write from scratch**. (The first five are the sourcing ladder drafted in `docs/2026-08-31-proposed-adr-software-development-component-adoption.md`, which is a proposal and not accepted. The sixth — author to someone else's design and credit it — is **not in that draft**; it was added in the 2026-09-01 conversation, along with a ruling that the ladder is not finalised. Names used for brevity, not as authority.)

**Preference.** Sourced rather than authored where possible, fewest changes. This was previously filed as a constraint; it is not one — it is chosen, and it rests on the ladder drafted in `docs/2026-08-31-proposed-adr-software-development-component-adoption.md`, which is a proposal and not accepted.

**What belongs here, and what does not.** A sourcing decision is a build-or-buy call about a **component we would include in the implementation**. It is not the same as **prior art**, which is where a requirement came from. ISO/IEC/IEEE 29148 and 12207, the Volere shell, Planguage, Fitzpatrick and the survey-methodology literature each generated requirements in this set; none is a component and none is bought. Their derivation lives in each requirement's *Source:* line and in `docs/research/2026-09-01-requirements-artifact-prior-art.md`, and is not restated here as a sourcing verdict. Only skills and skill components appear below.

### Adapt

| Source                                            | Licence    | What we take                                                                                                                                  | Why                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ------------------------------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `deliver-prd` — product-on-purpose/pm-skills      | Apache-2.0 | The Requirement Verification Map, the AI Behavior and Evaluation section, and the conditional-section discipline                              | **No longer the only model-behaviour source** — R39 comes from the OpenAI Model Spec and R22's clause from Anthropic's Usage Policy, both primaries ranking above a skill body. Re-tested 2026-09-01 against the post-R27 set and it still earns a row, for four things neither primary supplies: **refusal and abstention as named requirement rows** ("a model has no dependable default for either, so what the feature does when it should *not* answer is a requirement, not an implementation detail"); **per-component scoring**, because "an end-to-end pass rate hides which step failed"; **stating how the case set was sized as a method, never as a borrowed number**; and the conditional-section rule — "a PRD that omits a section its feature does not need is complete; a PRD that includes an empty one is not". None of the four is in the requirement set; they are implementation material for R39, not requirements themselves |
| `interview-me` — addyosmani/agent-skills          | MIT        | The explicit-yes gate with its enumerated false yeses, and the confidence-number-with-a-reason                                                | Its Step 5 enumerates what does **not** count as agreement — "Whatever you think is best", "Sounds good", silence followed by "okay let's start" — and nothing higher in the evidence set does: 12207 6.4.2.2(g) makes agreement a process outcome without saying what agreement looks like, and Fitzpatrick names the hollow yes but answers it with costly commitment. **Its own stop is declined** — "The 95% Confidence Stop" is a self-judged score, the same ground `requirements-clarity` was rejected on. **Its loop is not taken**: it fails R30, R5, R8 and R9 — one question at a time, a single guess, nothing written until the end, and no per-requirement confirmation. It does satisfy R31, the terminal restate                                                                                                                                                                                                                      |
| `brainstorming` — obra/superpowers                | MIT        | The shape of a process skill: a hard gate, a numbered checklist, a one-way ratchet, an anti-pattern table, a named handoff ritual             | Read at **v6.2.0**, the version installed on both harnesses. Four deltas: the classifier is dropped — Spike/Bounded/Architectural classifies code, and "bounded" is defined by whether the flow already exists in the repo, which a need has no equivalent of; the write moves to the top of the loop per R8; the anti-pattern rows are rewritten because upstream's argue against R2's decline; the ratchet is retargeted, so a started run never downgrades to a decline. That last idea comes from v6.3.0's path system — 6.2.0 has no paths and nothing to ratchet between                                                                                                                                                                                                                                                                                                                                                                        |
| `requirements-clarity` — softaworks/agent-toolkit | MIT        | Its **Do NOT activate when** list: a file path in the request, a code snippet, a named existing function, a bug with clear reproduction steps | The most operational decline test in the corpus, and additive to R2's rather than a duplicate: `neuroarxiv`/`adhd` supply questions to ask yourself, these are surface signals checkable without asking anything. All four say the request is already downstream of this phase. **Its 90/100 gate is declined**, and 50 of its 100 rubric points are the how                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |

### Take the idea — credited, not copied

| Source                               | What we take                                                                                                           | Serves                                                  |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| `shape-spec` — duthaho/claudekit     | "Ceremony is what scales, not the gate", and evidence never scaling to zero                                            | The invariant `brainstorming` implements without naming |
| `neuroarxiv` / `adhd` — UditAkhourii | The three-question pre-flight with explicit-invocation bypass; the isolation invariant; converge rather than shortlist | R2, R26's gate                                          |
| `framing-doc` — rjs/shaping-skills   | The per-line provenance audit with a delete rule. **No LICENSE file — idea only**                                      | R11, R13 (the only two it passes)                       |

### Defer

- **`spec-kit`** — trigger: it stabilises, or the phase needs a machine-checkable gate. Its v1.0.0 release notes disavow their own compatibility promise.
- **`helm-brief`, `matter-intake-scoping`, `incoming-request-advisor`** — their labelled-inference schemes overlap what Volere and 29148 already supply. Trigger: R12's three classes prove insufficient in use.

### Reject

A rejection here is of a **component**, never of a skill. Failing a requirement disqualifies the part that fails it and says nothing about the rest of the body — `requirements-clarity` moved to Adapt on exactly that ground, its score gate declined and its decline signals taken.

- **`requirements-clarity`'s 90/100 score gate** — LLM-judged, and 50 of its 100 rubric points are the how. The skill itself is an Adapt source.
- **spec-kit `/specify` as the phase** — *"Make informed defaults for unspecified details"* is the inverse of R9 and R31, which require per-requirement confirmation and a terminal restate. **Two earlier grounds are withdrawn**: a hard error on empty input and a three-marker clarification cap are in neither current preset, re-read 2026-09-01 — both are 23 lines, and `NEEDS CLARIFICATION` survives uncapped in `templates/spec-template.md`. The rejection now rests on the defaults clause alone.
- **`create-prd`, `alirezarezvani`'s PRD, `define-problem-statement`** — screened; nothing survives verification beyond R1 and one or two content slots. **Not re-read at component level.** These were rejected as skills, which is the error corrected above; the three lowest pass counts make a find unlikely, not impossible. Open.

## Open questions

**Scope of the artifact-content rules, ruled here because a review found the question live.** R15, R18, R24, R35, R37 and R38 govern the artifact the *skill produces*. **R40 is the exception and is not exempted**: this document's own sections were reordered to satisfy it on 2026-09-01, making it the only artifact rule with a compliant worked instance. They do **not** bind this document, which is an input to building that skill rather than an instance of its output. R4 and R9 were split on merit — a conjunction hides an untested half, and the sourcing screen demonstrated exactly that failure on R4 — not because R15 obliged it. A review that applies R15 to this document while declining to apply R18 to it is inconsistent; the consistent position is that neither applies.

- Do constraints belong before the requirements? 12207's activity order puts them first; readability puts them after. Currently after.

- Does each requirement carry its nature — decided, corrected, deferred, measured? Currently only exceptions are marked.

- **No compliant exemplar of the output exists, and R27 widened the gap.** The scope ruling above exempts this document from R15, R18, R24 and now R35, R37 and R38 — this document's requirements lean on their section headings, its prose carries obligations outside requirement statements, and no set-level consistency check has been run on it. So the only worked instance is exempt from **six** rules the skill must enforce — and the exemption is load-bearing: R2 joins three conditions with "or" against R15, and R19 uses "never" twice against 29148 5.2.7's totality terms. (29148 5.2.8 uses "never" too, which is why the exemption exists and why an exemplar is needed to show what does survive.) Ship a compliant sample artifact, or the skill is built against a specification never instantiated.

- ~~**Is R27 finished on this set?**~~ **Closed 2026-09-01**; `docs/research/2026-09-01-r27-completion.md` carries the result. The prediction that finishing it would repay itself held — R24's escape hatch and R28's ordering were confirmed at their primaries, and five requirements were found that no earlier pass had. The collision rule was **not** confirmed: the corpus that would have supplied it was refuted on transfer.

**Closed since drafting.**

*Do R26–R28 belong in a skill screen?* No. They are pipeline requirements; a pipeline is composed rather than sourced, and the universal failure measured the screen's granularity. Moved into the Pipeline section as a statement.

*Is R10 safe against acquiescence?* The disagreement is dissolved rather than adjudicated. Fitzpatrick's objection is to **verbal assent** as a termination signal — an utterance whose politeness meaning is indistinguishable from its agreement meaning. A token chosen in advance and never used conversationally is not that; it cannot be produced by politeness. 12207's process outcome is satisfied and Fitzpatrick's failure mode is closed, without needing his costly-commitment substitute.

## Evidence

Each phase section above links its own research note. Those paths are bare relative paths, deliberately. An earlier version instructed pinning them to a commit against the coming reorganisation; that was wrong for this repo, whose practice is to rewrite links when things move — #90 did exactly that. (#92 is not a witness for it: it swept titles and a retired prefix, and its resolution states "URLs and repo-slug links untouched".) A pinned link survives the move by pointing at a superseded copy, which is worse than a path that breaks loudly and gets fixed.

Primary sources read directly: ISO/IEC/IEEE 29148:2018 (`sources/29148-2018.pdf`, clauses 5.2.5–5.2.8); ISO/IEC/IEEE 12207:2017 (`sources/12207-2017.pdf`, clauses 6.3, 6.4.2, 6.4.3); the Volere requirements shell (Edition 11, 2006, for the fields; Edition 16, 2012, for the template); **added 2026-09-01, each downloaded and string-matched locally** — ECSS-E-ST-10-06C; the FAA Requirements Engineering Management Handbook DOT/FAA/AR-08/32; NIST AI 100-1; the INCOSE Guide for Writing Requirements V3.1 (from a university mirror, **not** the publisher); FAR Parts 10, 11 and 16 at acquisition.gov; the OpenAI Model Spec 2026-08-18; Anthropic's Usage Policy; and IMDRF SaMD N10, N12, N23 and N41 (`sources/imdrf-*.pdf`, supplied by the author); the bodies of `brainstorming`, `interview-me`, `shape-spec`, `write-spec`, `deliver-prd`, `define-problem-statement`, `requirements-clarity`, `helm-brief`, `framing-doc`, `matter-intake-scoping`, `incoming-request-advisor`, `neuroarxiv`, `adhd`, `to-spec`, `grilling`, `research`, `writing-plans`, `subagent-driven-development`, and spec-kit's `specify.md` and `spec-template.md`.

**Every source a requirement rests on has now been read.** The six that had not been — R5 (Willis; Pew), R6 and R13 (Fitzpatrick), R9 (Beyer and Holtzblatt), R16 and R17 (Gilb, both since retired, with Gilb's Meter definition surviving inside R14) — were supplied by the author on 2026-09-01 and read from the text. Reading them **refuted three claims this document had been making**: a Fitzpatrick sentence that does not exist in the book, Willis terminology absent from both his guides, and R17's citation of Planguage's levels as `Must` and `Plan` when they are `Fail` and `Goal`. Two things remain unread and nothing depends on either: Willis's 2005 Sage book, which is the only place the withdrawn probing labels could live, and the two unnamed primaries behind R6's convergence claim.

Evidence ladder applied: standards-body consensus documents rank highest; then regulatory text; then published research; then named practitioner methods; then upstream artifacts read directly; and this project's own working documents lowest — primary about themselves, and evidence about nothing else.
