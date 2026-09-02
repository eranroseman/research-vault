# Requirements: writing-requirements (the pre-spec phase)

> **For agentic workers:** REQUIRED SUB-SKILL: `writing-specs`. This document is the input to the design phase, not a design.
>
> **Status:** draft, 2026-09-01, revised the same day after review. **Not confirmed** — the gate this document specifies has not been run on this document. Identifiers are never changed and never reused, which is why splitting R4 and R9 produced R30 and R31 rather than renumbering.
>
> **Delete when** `writing-requirements` ships and its skill body carries these requirements, or when the design is abandoned. This document is scaffolding, not a record: git history holds it after deletion. Precedent — `553ae6f`, "delete 14 merged/abandoned superpowers plan files". A never-maintained file sitting at a stable path is the stale record that deletion exists to prevent.
>
> **Sequencing, ruled 2026-09-01:** build now, not after `writing-specs`. `writing-requirements` is written here, drawing text from four skills rather than vendored from any one — so it never merges upstream, was never a drift surface, and waiting for `writing-specs` buys nothing. The two are not siblings and are not required to match; each carries what its own altitude needs. **The gate on building is R27, not sequencing** — four corpora remain unapplied and their leads predicted three later-confirmed defects.
>
> **Durable home** is the `software-development` repository, which does not exist yet. #59 owes its **structure decision**, not the repository — its own body puts building it out of scope. This tree is the working home while the design dossier lives here, not the destination.

## Problem

I build software with AI agents, alone, across three workloads: my own tooling, a research vault, and HITL health-and-wellness coaching apps. The process I want runs from "I have this idea" to working software.

The process I have starts one step too late. `writing-specs` takes an idea and produces a technical design; it assumes I already know the what. So the what and why never get written down — it asks me for purpose, constraints and success criteria every time, steers the design with them, and records none of them.

The cost lands on my attention. An agent starts work carrying assumptions I never gave it and it never declared, and I find them by interrogating it three rounds later. Interviews are not the cost — I will take an agent interviewing me all day if that gets the job right. Interrogation is the cost.

The absence is not hypothetical. Four artifacts compensate for it somewhere else. Three are in my roster: `brainstorming` asks the questions in a conversation that discards the answers; `rethink-audit` carries it as rung one of an audit method; this repo's foundation spec puts it in §1 of the design document. The fourth, mattpocock's `to-spec`, is neither installed nor adopted here — it puts Problem Statement and User Stories inside a spec template, and its author documents the resulting deformation.

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

**The headline finding is an absence.** Ten agent frameworks were surveyed and none has this phase. Five independent implementations each compensate for the gap inside a downstream artifact instead. What the older traditions do have, they had early: the Volere shell carried Description, Rationale, Originator and Fit Criterion per requirement in the 1990s, which makes the modern six-field convergence a lossy rediscovery rather than a new result.

| Source                      | What it gave                                                                             | Requirements  |
| --------------------------- | ---------------------------------------------------------------------------------------- | ------------- |
| ISO/IEC/IEEE 29148:2018     | 5.2.5 characteristics; 5.2.7 forbidden terms; 5.2.8 identifier rule                      | R15, R18, R19 |
| ISO/IEC/IEEE 12207:2017     | Agreement as a process outcome; abuse-and-failure scenarios; the four constraint sources | R10, R22, R23 |
| Volere requirements shell   | Description, Originator, Fit Criterion                                                   | R11, R14      |
| Planguage — Gilb            | Scale and meter; `Must` versus `Plan`                                                    | R16, R17      |
| Fitzpatrick, *The Mom Test* | Anchor in specific past events; verbatim marked as verbatim                              | R6, R13       |
| Willis; Pew Research        | Multi-possibility probing over single-possibility                                        | R5            |

None of these is a sourcing decision. They generated requirements; they are not components and nothing is bought from them. The sourcing section below holds only skills and skill components.

**One requirement has no anchor here.** The phase's own success criterion is stated by no tradition surveyed — named rather than stretched onto a near-miss.

## Competitive analysis

Ran **after** the requirements were drafted, against six corpora, and edited the set. It is presented **before** them because the set shown below is the post-update one: several requirements exist only because this pass found them, so reading the requirements first would leave those unexplained. Full verdicts: `docs/research/2026-09-01-pre-spec-competitive-analysis.md`.

**What it changed.** The largest correction was to the interview loop: the guess-attached question is backward-looking in both traditions that use it, and attaching a forward guess to an open question is a mutation with measured harm — acquiescence bias, worse with an interviewer present. Willis's multi-possibility probing replaced it as R5. Anchoring elicitation in specific past events entered as R6, the single most-agreed rule in the discovery corpus. R9 was recalibrated because confirmation is continuous in both traditions that use it, not concentrated into one terminal restatement. Verbatim-marked-as-verbatim entered as R13, and a declared risk tier as R3. R7's question-cap survived a null result in its favour — nobody caps question count.

**Two disagreements were recorded rather than resolved.** Fitzpatrick argues verbal assent is precisely the data type that must not terminate elicitation; 12207 6.4.2.2(g) makes stakeholder agreement a process outcome. R10 takes the standards position with the dissent noted.

**Status: complete.** Two of six corpora were read in full in the first pass. The remaining four — LLM behaviour specifications, systems and safety engineering, procurement, and testable-at-scale formats — were read properly on 2026-09-01 and are recorded in `docs/research/2026-09-01-r27-completion.md`. That pass produced 74 findings, sent 16 to adversarial verifiers, and **9 survived**: five new requirements (R35–R39) and four recalibrations (R21 in part, R22, R24, R25, R28).

**Two things it did not support.** R24's missing escape hatch was confirmed, but not on the grounds first recorded — the three procurement regimes cited are not independent, all descending from WTO GPA Article X. And the predicted two-tier gap — that the sourcing screen is mandatory-only where procurement forbids a mandatory tier standing alone — **is not established**. The corpus's decision rule for the split was verified and refuted, and the surviving finding rests on a goals section this document does not have, asserted falsely in my own guard block. Nothing from the testable-at-scale corpus is applied: all four of its verified findings broke on generalisation or transfer despite exact quotes.

## Requirements

**R34 is reserved, not issued.** It is held for the harness-support requirement flagged in Constraints, pending a ruling. Identifiers are never reused (R19), so the gap between R33 and R35 is deliberate and does not mean a requirement was deleted.

Source vocabulary, defined by **origin** rather than by confirmation status: `elicited` — stated directly, quoted where short. `inferred` — derived from what was stated. `assumed` — brought from the agent's general knowledge rather than from anything said. Otherwise a named document. Any of the three may be confirmed or not; confirmation is tracked separately, because defining a class by confirmation status leaves agent-supplied-and-confirmed material with no label — which is what R12's three classes and R23 both need.

### Skill behaviour

**R1** — Accepts a need arriving unframed in conversation.
*Fit:* a bare sentence with no user, no success criterion and no constraint produces a first turn, not an error.
*Source:* FAR 10.002(a), FAC 2026-01 — "Acquisitions begin with a description of the Government's needs stated in terms sufficient to allow conduct of market research." A rough description is the legitimate entry state, not a defect. Verified locally 2026-09-01. Previously `elicited` — "the usual route is chat → spec → plan" — which is still the origin, now with a primary behind it.

**R2** — Declines when there is no real question, the effort is small, or the approach is already chosen.
*Fit:* three questions, each answerable no; any no aborts with one sentence naming how to invoke it deliberately.
*Source:* `neuroarxiv` and `adhd` pre-flight gates, both with an explicit-invocation bypass.

**R4** — Asks questions in dependency order.
*Fit:* no question is asked whose answer hinges on another still open in the same round.
*Source:* `mattpocock/skills` commit `a4b2009a` — "Same 13 questions land in ~3 rounds instead of 13."

**R30** — Does not spend separate round-trips on questions that do not depend on each other.
*Fit:* a set of mutually independent questions is put in one round, not serialised.
*Source:* as R4. Split out because the two were joined by a conjunction and only the first was tested — the sourcing screen failed `interview-me` on the second half while R4's written fit would have passed it.

**R5** — Where a hypothesis is offered before an answer exists, offers the plausible alternatives rather than a single guess.
*Fit:* no question presents one guess as the expected answer.
*Source:* Willis — single-possibility probing biases, multi-possibility probing is the remedy. Pew — acquiescence is worse with an interviewer present.

**R6** — Anchors questions in specific past events rather than opinions, generalities or predictions.
*Fit:* each question asks what happened, not what would.
*Source:* Fitzpatrick, *The Mom Test* — recoverable. Reported by the competitive-analysis pass as the most-agreed rule in the discovery corpus, converged on by "three independent primaries"; **two of the three were never named and are unrecovered**. Treat the strength of the convergence claim as unverified.

**R7** — Places no cap on the number of questions or clarification markers.
*Fit:* no number bounds questioning anywhere in the skill.
*Source:* a **null result** from the competitive-analysis pass, which is evidence rather than an absence of it: no practice surveyed caps question count, and every one caps something adjacent instead — learning goals per person-type, session length, question density. Searching 29148 and 12207 for any cap on elicitation effort returned nothing, consistent with that. Competitive-analysis derived, not prior art; no prior art exists to derive it from. The author's position — "I prefer agents interviewing me all day long if that is what is needed to get the job right" — is the origin.
*Note:* drove no rejection in the sourcing screen except jointly with R1. May be describing the field rather than screening it.

**R8** — Writes each requirement as its answer settles, not in one pass at the end.
*Fit:* a requirement exists in the artifact before the interview ends.
*Source:* FAA REMH DOT/FAA/AR-08/32 §2.11.7, verified locally 2026-09-01 — "Rationale should be collected along with the development of the requirement… This ensures that the justification is captured by the author while he or she is thinking about it… it is much simpler to record the rationale when the latency was being computed than to try to re-engineer the reasoning later." The reason given is the author's attention, which is this requirement's reason too. Origin: `elicited` — "interview user for why and what, write requirement, verify, repeat until done."

**R9** — Confirms each requirement when it is written.
*Fit:* no requirement enters the artifact unconfirmed.
*Source:* contextual inquiry's *Interpretation* principle; qualitative research's *member checking*. Both are continuous rather than terminal. `assumed` — the rendering is mine.

**R31** — Restates the accumulated set before terminating.
*Fit:* the final restate covers every requirement written, not only those settled last.
*Source:* ECSS-E-ST-10-06C 5.2, verified locally 2026-09-01 — "The customer assesses the entire set of technical requirements for correctness, consistency and suitability for the intended use." The task appears **twice**, as F1.3 and again as F1.9, each immediately before a release task, so a whole-set assessment before terminating is a distinct process step rather than a by-product of per-item confirmation. INCOSE GtWR V3.1 places five characteristics at set level for the same reason — C10 Complete, C11 Consistent, C12 Feasible, C13 Comprehensible, C14 Able to be Validated — properties that cannot be checked one requirement at a time. Split from R9 because continuous confirmation and a terminal restate are two obligations and a skill could satisfy either alone; that split is now backed rather than asserted.

**R10** — Terminates on a confirmation signal I chose in advance and do not use conversationally.
*Fit:* the signal is agreed before the phase runs and is distinguishable from assent — "sounds good", "sure", "looks right" and silence do not match it. No score and no count substitutes for it.
*Source:* ISO/IEC/IEEE 12207:2017 6.4.2.2(g) — "Stakeholder agreement that their needs and expectations are reflected adequately in the requirements is achieved." `assumed` — adopting it here is unconfirmed. The prohibition on an LLM-judged score as the gate is a decision, not evidence; no standard has a position on it.

**R37** — Before the confirmation gate, checks the accumulated set as a set: no two requirements assign different outcomes to the same subject under conditions that can hold at once, nothing is stated twice, and the same term means the same thing throughout.
*Fit:* for each pair of requirements sharing a subject, the run states whether their conditions can both hold, and where they can, that their outcomes agree. A collision is resolved or recorded under R25 before the gate.
*Source:* R27, survived verification. ECSS-E-ST-10-06C 7.2.3d — "The technical requirements shall be consistent (e.g. not in conflict with the other requirements within the specification)" — with FAA REMH 2.8.4 giving the operable form, "only one ideal value is assigned to each controlled variable and each internal variable for every possible system state", and INCOSE C11 adding terminology homogeneity. Every rule in the set to this point governs a requirement in isolation; nothing governed the set.

### Artifact content

**R3** — Records which workload and risk class the need belongs to, with the reason.
*Fit:* the artifact states the class; a reader can tell a coaching-app feature from a tooling decision without reading further.
*Source:* three primaries, all verified locally 2026-09-01. NIST AI 100-1 MAP 1.1 documents "intended purposes… and prospective settings in which the AI system will be deployed" and places it before the go/no-go. FAR 10.002(b)(1) — "The extent of market research will vary, depending on such factors as urgency, estimated dollar value, complexity" — makes the class the input that scales the process, not a bare fact. INCOSE GtWR V3.1 R29 classifies *per requirement* as a completeness search device. **R3 takes the weakest of the three forms**: one class for the whole need, used as a routing label. Previously `assumed`, citing four regulatory regimes none of which was read; that claim is withdrawn and unreplaced — FDA, IEC 62304 and IMDRF were not reached.

**R11** — Each requirement carries its source.
*Fit:* no requirement traces to nothing.
*Source:* Volere requirements shell, `Originator`; 12207:2017 6.4.2.2(i).

**R12** — Distinguishes what I said, what the agent inferred from what I said, and what the agent brought from general knowledge.
*Fit:* three distinguishable classes, not two.
*Source:* `matter-intake-scoping`'s four-level provenance scheme. 12207 treats implicit needs from domain knowledge as a legitimate input, so this marks rather than forbids.

**R13** — Marks verbatim material as verbatim, distinct from paraphrase.
*Fit:* a reader can tell my words from the agent's summary of them.
*Source:* Fitzpatrick, *The Mom Test*, reported as imposing a provenance discipline of this shape. **Paraphrase, not verbatim** — the book is not in the read-directly list below, and the phrasing previously carried here in quotation marks came from an agent's report rather than from the text. Verify before quoting.

**R14** — Each requirement carries a fit criterion: a measurement testing whether a solution matches it.
*Fit:* Volere's own test. Per requirement, not per goal and not per document.
*Source:* Volere requirements shell — "A measurement of the requirement such that it is possible to test if the solution matches the original requirement."

**R15** — Each requirement states a single capability, characteristic, constraint or quality factor.
*Fit:* no conjunction joins two.
*Source:* ISO/IEC/IEEE 29148:2018 5.2.5.

**R16** — A quality requirement carries a scale and a meter.
*Fit:* no quality stated without how it is measured.
*Source:* Gilb, Planguage.

**R17** — Where a floor exists, the threshold is two-level: the level below which it fails and the level aimed at.
*Fit:* two numbers.
*Source:* Planguage, `Must` and `Plan`.

**R18** — Forbids the vague terms 29148 5.2.7 enumerates.
*Fit:* no superlatives, subjective language, vague pronouns, ambiguous adverbs, ambiguous logical statements, open-ended non-verifiable terms, comparatives, loopholes, totality terms or incomplete references.
*Source:* ISO/IEC/IEEE 29148:2018 5.2.7 — "Vague and general terms shall be avoided."

**R19** — Requirement identifiers are never changed and never reused.
*Fit:* an R-number cited in a later round means what it meant in the first.
*Source:* ISO/IEC/IEEE 29148:2018 5.2.8.2.

**R20** — Records problem and solution from my perspective.
*Fit:* both describe an experience, not a system property.
*Source:* `to-spec`'s first half; `helm-brief`'s test — "Must describe a user experience, not a product gap."

**R21** — Records the boundary of the need: what falls inside it and what falls outside.
*Fit:* a reader can place a candidate feature on one side or the other without asking. A list of things not being built does **not** satisfy it.
*Source:* `interview-me`, `shape-spec` and `helm-brief` independently. Reframed from "records what is excluded" on 2026-09-01, on the author's ruling that a requirements document does not contain a list of non-goals — the four items removed from this document's own Out of scope section were definitional, not chosen. R27 corroborates from two corpora, which frame the item as a boundary rather than as an exclusion list; that finding was not itself verified, so the ruling is the authority and the corpora are support.

**R22** — Records constraints that bind this need, including sourcing decisions already binding, and — where the product calls a model — the provider's acceptable-use policy.
*Fit:* each is falsifiable, and each passes 29148 3.1.7 — a constraint is an *"externally imposed limitation… imposed on the solution by force or compulsion"*, so anything that could have been decided otherwise is a requirement and not a constraint. Where the provider's policy defines use-case classes, the artifact states which class this need falls in and quotes the conditions that class triggers, or records that no class applies and why.
*Source:* 12207:2017 6.4.2.3(d.1) — constraints include "required use of defined enabling, legacy, or interfacing systems" and "unavoidable consequences of existing agreements". The provider clause is R27's, survived verification: Anthropic's Usage Policy requires that for High-Risk use cases "a qualified professional in that field must review the content or decision prior to dissemination or finalization", classes "therapy, mental health" as High-Risk, and carves out "advice on sleep, stress, nutrition, exercise" — a boundary running through the coaching-app workload that nothing in this set could previously see.

**R23** — Generates requirements from abuse and failure scenarios, not only from stated needs.
*Fit:* the artifact contains at least one requirement nobody asked for.
*Source:* 12207:2017 6.4.2.3(c.1) — "Abuse and failure scenarios highlight the need for additional functional requirements."

**R24** — Contains no architecture, components, phases or estimates, except where no functional or performance statement can make the requirement understood.
*Fit:* nothing in the **requirement list** would change if the implementation approach changed. Scoped to the requirements rather than the whole artifact: R28 puts sourcing verdicts in their own section, and those are approach decisions by definition. Both traditions draw the line the same way — sourcing belongs in the document, not in a requirement.
*Source:* 29148:2018 5.2.7 — "Requirements should state 'what' is needed, not 'how'." A `should`, with an acknowledged exception at lower decomposition levels. The exception's form is R27's, survived verification: PCR 2015 reg 42(13) permits naming a specific make "on an exceptional basis, where a sufficiently precise and intelligible description… is not possible, in which case the reference shall be accompanied by the words 'or equivalent'". Where the exception is used here, the requirement names the property actually required and marks the named thing as an example, not a choice. One sub-claim was struck in verification: PCR, the Procurement Act 2023 and FAR Part 11 are **not** three independent regimes — all descend from WTO GPA Article X. The independent second leg is INCOSE and ECSS, which state the same exception inside the rule.
*Note:* it did screen. Four of twelve candidates claimed it — `interview-me`, `shape-spec`, spec-kit `/specify`, `framing-doc` — and eight failed. An earlier note here claimed the opposite and was false against the screen's own table.

**R25** — Records open questions, exempt from the completeness count.
*Fit:* an artifact with open questions can still be confirmed, and each open question carries the downstream point by which it must be resolved. A reader can proceed past every open question without contacting the author.
*Source:* 29148:2018 5.2.6 permits TBx during evolution — "Resolution of the TBx designations may be iterative and there is an acceptable timeframe for TBx items" — and forbids them at completion. The resolution-point half is R27's, survived verification: FAR 16.603-2(c) lets a binding instrument carry an unresolved item only against a deadline — "definitization of the contract within 180 days… or before completion of 40 percent of the work to be performed, whichever occurs first". The exemption holds because this artifact is never the completed set: it is an input to a design phase that resolves the open items, and it is archived rather than contracted.

**R33** — In a non-interactive context, names the questions it would have asked and stops, rather than answering them itself.
*Fit:* a run with no user produces a question list and no requirements.
*Source:* OpenAI Model Spec 2026-08-18, verified locally 2026-09-01. Guideline: "Consider uncertainty, state assumptions, and ask clarifying questions when appropriate." Its worked example "Ambiguous request where a missing artifact is likely" makes the compliant response name what is missing — "I think you might have forgotten to paste or upload the text you want me to revise" — and makes proceeding by supplying the content yourself the violation. **Lowest usable rung**: a vendor's specification of its own models, not standards-body consensus. Origin: `elicited`, as a scope note; numbered here because it is behaviour, not scope. The subagent run of 2026-09-01 is the worked example — and it detected the absent user because it was told, not because anything in this design would have.

**R32** — Records whether the confirmation gate has passed.
*Fit:* a cold session opening the file can tell a confirmed artifact from an abandoned one without asking.
*Source:* NIST AI 100-1, verified locally 2026-09-01: an "explicit process for making go/no-go system commissioning and deployment decisions" is a named benefit the framework exists to produce, and it is placed after context is established and before building — this requirement's exact position. Previously `inferred` from R8, R10 and R29 interacting, which remains the derivation of its necessity here. R8 guarantees a partial artifact exists on disk mid-interview; R29 promises cold-session consumption at a stable path; R10 defines a gate whose outcome nothing currently records. Without this, `writing-specs` cannot distinguish a set I confirmed from one I walked away from.

**R35** — Each requirement is complete on its own: its meaning does not depend on its section heading, on neighbouring requirements, or on surrounding prose.
*Fit:* lift any single requirement out of the artifact, with no other text, and a reader who has not seen the artifact can say what is required and what would violate it — without asking what "it" or "the system" refers to.
*Source:* R27, survived verification. ECSS-E-ST-10-06C 8.2.8a — "A technical requirement shall be self-contained", noting it "does not require additional data or explanation to express the need" — and INCOSE GtWR V3.1 R25, "Avoid relying on headings to support explanation or understanding of the requirement." Load-bearing here because R14 turns each requirement into a standalone test.

**R36** — Records environmental assumptions in their own section, separate from constraints: claims about the world outside the system that the requirements depend on and that no party is obliged to make true.
*Fit:* for each assumption, a reader can name who or what would have to change for it to become false, and can state that nobody on this project controls that. A statement failing that test is a constraint under R22, not an assumption.
*Source:* R27, survived verification. FAA REMH DOT/FAA/AR-08/32 §2.4 — "These are actually requirements levied by the system on its environment… Failure to identify the environmental assumptions and the subsequent misuse of the system is a common cause of system failure." This document's own Assumptions section was added on 2026-09-01 from the competitive analysis's headline; this is the primary behind it, read directly.

**R38** — Marks obliging text distinctly from explanatory text.
*Fit:* no sentence outside a requirement statement carries a modal of obligation. Where explanatory text turns out to carry something the system has to do, that thing is promoted to a requirement or the artifact does not pass the gate.
*Source:* R27, survived verification. ECSS-E-ST-10-06C 7.2.7a — "If a clause is stated to be informative or descriptive, then this clause shall not contain any requirement or recommendation" — with 8.3.2 fixing the verbal forms. *The agent's proposed wording also assigned `should` to goals; dropped, because there is no goals section and that clause came from a premise this project's own guard block supplied falsely. Recorded in the R27 note.*

**R39** — Where the product's user-facing output is generated by a model, records the required model behaviour for each sensitive interaction the product can reach, and for each states whether it accepts or overrides the provider's published default.
*Fit:* for every sensitive-domain behaviour the provider publishes at an overridable level and this product's flows can reach, the artifact carries an accept-or-override verdict naming the provision. A product with such flows and no verdicts fails. Does not apply where no model output reaches a third party, which exempts the research vault and personal tooling.
*Source:* R27, survived verification. OpenAI Model Spec 2026-08-18 tags "Provide information without giving regulated advice" **Developer** and "Support users in mental health discussions" **User** — both below Root, so a developer may override them and silence accepts them. **What transfers is the structure**, not the provision list: published defaults exist, are overridable, and bind by silence. The list is OpenAI's and does not govern a product running on Claude; the binding instrument there is the Usage Policy, under R22.

**R40** — The artifact's sections follow the order of the phases that produced them, and each carries or links the evidence that phase produced.
*Fit:* a reader can name which phase produced each section and reach that phase's evidence from inside it, without an index. A section for a phase that never ran does not appear. Where an output depends on a phase that ran after it — the requirement set is the post-competitive-analysis one — presentation order differs from run order and the section says so.
*Source:* ECSS-E-ST-10-06C Annex A, **verified locally 2026-09-01** — a normative Document Requirements Definition mandating the table of contents, section by section, which is the same claim as "sections follow the phases" made by a standards body. No longer an unverified lead. The author's rulings of 2026-09-01 remain the origin: "the docs sections should follow the process phases to reflect the work that was done", and that prior art and competitive analysis precede the requirements "as some of the reqs are derived from the comp analysis".

### Pipeline

These three are requirements on the **phase**, not on any single skill. Every candidate failed all three — which measures the granularity of the screen, not a gap in the field. A skill does not contain three sub-steps that are themselves skills; a pipeline composes them. They are satisfied by the composition and are not screening criteria for any component of it.

**Delivery, ruled 2026-09-01: one skill with three internally-gated phases**, each dispatching an isolated subagent. Three named sub-skills would put three descriptions with exactly one caller each into the router's match pool — the same failure `grilling`'s description suppression was fighting. Delegating to the installed `research` skill fails R26's fit, which requires patterns to arrive already shaped as requirements rather than as candidates to weigh. The one real cost — phases not independently re-runnable — is met by an optional entry argument naming a phase, so re-running sourcing alone does not mean re-entering the loop.

**R26** — Runs a prior-art step before writing requirements, behind a gate.
*Fit:* patterns found arrive as requirements, not as candidates to weigh.
*Source:* two primaries, verified locally 2026-09-01. FAR 10.001(a)(2)(i) mandates the ordering in the imperative — agencies shall conduct market research "Before developing new requirements documents" — and FAR 10.002(a) supplies the gate's entry condition, a need described well enough to research against: enough to search on, not enough to specify. ECSS-E-ST-10-06C 5.2 states the gate's *exit* condition — the concept-exploration step "is needed in phase 0 for space projects with **low heritage**", so high heritage skips it. Origin: `elicited`. The cost of skipping it was paid in this session.

**R27** — Runs a competitive-analysis step that edits the requirement set before the confirm gate.
*Fit:* its output is edits to requirements — added, recalibrated, dropped, confirmed — not verdicts on competitors.
*Source:* ECSS-E-ST-10-06C 5.2, verified locally 2026-09-01 — "The second step consists of the exploration among the different possible concepts… This version is progressively drafted from the preliminary TS and takes into account the induced constraints from the possible concepts." A concept step that **amends** an earlier requirement baseline rather than replacing it is this standard's normative two-baseline structure, which is the ordering chosen here. Origin: `elicited` — "how my requirements compare to other solutions."

**R28** — Runs a sourcing step after requirements settle, whose verdicts land in their own section rather than as requirements; where the verdict is that nothing available satisfies a requirement, the step re-opens that requirement.
*Fit:* a reader can tell which came first, and no verdict of "nothing available" leaves the artifact without either a restatement of the named requirement or an explicit decision to build it bespoke, landing before the confirmation gate. Verdicts are about **components**, never whole skills: a component failing one requirement says nothing about the rest of a body.
*Source:* 29148:2018 5.2.5 NOTE 1 names "a system that can be bought rather than made" as an inappropriate requirement; Volere places Off-the-Shelf Solutions at section 19, separate from Functional Requirements at 9. The re-opening half is R27's, survived verification: FAR 10.002(c) runs market research **both** ways — "agencies shall reevaluate the need… and determine whether the need can be restated to permit commercial products… to satisfy the agency's needs." An earlier version of this requirement was a one-way valve, which the primary is not. The component-level clause is the author's ruling of 2026-09-01.

### Integration

**R29** — Output lands at a stable path with a header naming its consumer.
*Fit:* `/writing-specs @path` works from a cold session.
*Source:* ECSS-E-ST-10-06C Annex A (normative) A.2.1 \<1>, verified locally 2026-09-01 — "The TS shall contain a description of the purpose, objective, content and the reason prompting its preparation." The header carries four things there and one here. **The gap is "the reason prompting its preparation"**, which is precisely what an artifact archived and never maintained loses first. Previously the house convention alone, specified verbatim in `writing-plans`' plan header; that remains the format, now with a standard behind the obligation.
*Note:* every candidate failed it, so it screened nothing — the same shape as R26–R28. An obligation on what we build, not a discriminator among what we might take.

## Constraints

**Test applied**, ISO/IEC/IEEE 29148:2018 3.1.7: a constraint is an *"externally imposed limitation… imposed on the solution by force or compulsion"*. Could it have been decided otherwise? If yes it is a requirement, not a constraint.

- Runs on Claude Code and Codex. **Fails the test and is pending promotion to R34** — the harnesses are pre-existing, but supporting both is a decision and is testable; shipping Claude-only was available. Held here until the number is issued, because identifiers are never reused.
- **Archived on handoff, never maintained — inherited, not chosen here.** This is how the whole superpowers workflow operates: specs and plans are archived once implemented, and this artifact sits in the same pipeline. Drift from the product is expected. Two competitive-analysis findings push against it — a controlled-record obligation under design controls if a coaching-app feature crosses the wellness boundary, and the absence of any named re-run trigger. Neither is answerable inside this phase; both are about the pipeline. **Neither has a tracker home yet** — they sit in the competitive-analysis note, which is temporary, and which ticket takes them (#60, #62 or #63 territory) is unresolved. Carried as a leftover for the #81 post, not silently absorbed.
- `writing-specs` is the only consumer. (An earlier version added "and it is not modified by this phase", which is definitional rather than imposed.)
- **Enumerability is a pipeline obligation, and it is not discharged here.** `writing-plans` never reads this artifact — its Self-Review walks the *spec* against the *plan*: "Can you point to a task that implements it? List any gaps." So each requirement must survive into the spec in a form that check can walk. **Nothing in this phase can guarantee that**, because the guarantee belongs to `writing-specs`' own design, which #60 and #62 own. Filed there as an obligation, not left here as an aside. (An earlier version claimed `writing-plans` consumes this artifact directly; it does not.)
- MIT and Apache-2.0 attribution is owed wherever text is taken substantially, regardless of how the maintenance relationship is described. The licence is the constraint — 29148's own example is *"laws of a particular country"* — and carrying the attribution is a requirement derived from it, currently unnumbered.

## Sourcing decisions

Sourcing sits in this phase because `writing-specs` cannot hold it — its approach comparison is architectural alternatives inside your own tree, not build-or-buy. **Trigger to move: `writing-specs` gains build-or-buy comparison.**

Full screen, method and per-candidate failures: `docs/research/2026-09-01-pre-spec-sourcing-screen.md`.

**Screen result, 2026-09-01.** Twelve candidates screened pass/fail against the twenty-nine requirements that existed at the time, one isolated agent each, every result adversarially verified. **R30, R31 and R32 post-date the screen and no candidate has been tested against them.** R30 exists to preserve a measured failure: the screen failed `interview-me` on the batching half of the old R4, and the narrowed R4's fit would no longer record it. No candidate ever passed R4 — it appears in no pass column — so nothing was flipped by the split. Claimed passes ran three to eight; after verification **nothing exceeds three of twenty-nine**. `write-spec` is the only candidate passing **R14** after verification, which is the useful part of that result: it establishes the per-requirement fit criterion is achievable in a skill body, not just in a standard. It earns no adapt row. Its acceptance-criteria section is 29148 5.2.7 (forbidden terms), 29148 5.2.5 (independently testable), 12207 (negative and edge cases), Volere (the criterion itself) and BDD's Given/When/Then, each already sourced here from its origin rather than from an intermediary. What is genuinely its own is the P0/P1/P2 three-tier priority scheme, which this set declines.

That measurement closes the top three treatments — **install a plugin as-is**, **fork it and keep merging**, **copy it frozen** — since each takes something failing at least twenty-six musts.

What remains is **copy plus a delta**, **author to someone else's design and credit it**, or **write from scratch**. (The first five are the sourcing ladder drafted in `docs/2026-08-31-proposed-adr-software-development-component-adoption.md`, which is a proposal and not accepted. The sixth — author to someone else's design and credit it — is **not in that draft**; it was added in the 2026-09-01 conversation, along with a ruling that the ladder is not finalised. Names used for brevity, not as authority.)

**Preference.** Sourced rather than authored where possible, fewest changes. This was previously filed as a constraint; it is not one — it is chosen, and it rests on the ladder drafted in `docs/2026-08-31-proposed-adr-software-development-component-adoption.md`, which is a proposal and not accepted.

**What belongs here, and what does not.** A sourcing decision is a build-or-buy call about a **component we would include in the implementation**. It is not the same as **prior art**, which is where a requirement came from. ISO/IEC/IEEE 29148 and 12207, the Volere shell, Planguage, Fitzpatrick and the survey-methodology literature each generated requirements in this set; none is a component and none is bought. Their derivation lives in each requirement's *Source:* line and in `docs/research/2026-09-01-requirements-artifact-prior-art.md`, and is not restated here as a sourcing verdict. Only skills and skill components appear below.

### Adapt

| Source                                            | Licence    | What we take                                                                                                                                  | Why                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| ------------------------------------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `deliver-prd` — product-on-purpose/pm-skills      | Apache-2.0 | The Requirement Verification Map, the AI Behavior and Evaluation section, and the conditional-section discipline                              | The only source with model-behaviour requirements tied to evidence — needed for the coaching-app workload                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `interview-me` — addyosmani/agent-skills          | MIT        | The explicit-yes gate with its enumerated false yeses, and the confidence-number-with-a-reason                                                | Its Step 5 enumerates what does **not** count as agreement — "Whatever you think is best", "Sounds good", silence followed by "okay let's start" — and nothing higher in the evidence set does: 12207 6.4.2.2(g) makes agreement a process outcome without saying what agreement looks like, and Fitzpatrick names the hollow yes but answers it with costly commitment. **Its own stop is declined** — "The 95% Confidence Stop" is a self-judged score, the same ground `requirements-clarity` was rejected on. **Its loop is not taken**: it fails R30, R5, R8 and R9 — one question at a time, a single guess, nothing written until the end, and no per-requirement confirmation. It does satisfy R31, the terminal restate |
| `brainstorming` — obra/superpowers                | MIT        | The shape of a process skill: a hard gate, a numbered checklist, a one-way ratchet, an anti-pattern table, a named handoff ritual             | Read at **v6.2.0**, the version installed on both harnesses. Four deltas: the classifier is dropped — Spike/Bounded/Architectural classifies code, and "bounded" is defined by whether the flow already exists in the repo, which a need has no equivalent of; the write moves to the top of the loop per R8; the anti-pattern rows are rewritten because upstream's argue against R2's decline; the ratchet is retargeted, so a started run never downgrades to a decline. That last idea comes from v6.3.0's path system — 6.2.0 has no paths and nothing to ratchet between                                                                                                                                                   |
| `requirements-clarity` — softaworks/agent-toolkit | MIT        | Its **Do NOT activate when** list: a file path in the request, a code snippet, a named existing function, a bug with clear reproduction steps | The most operational decline test in the corpus, and additive to R2's rather than a duplicate: `neuroarxiv`/`adhd` supply questions to ask yourself, these are surface signals checkable without asking anything. All four say the request is already downstream of this phase. **Its 90/100 gate is declined**, and 50 of its 100 rubric points are the how                                                                                                                                                                                                                                                                                                                                                                     |

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
- **spec-kit `/specify` as the phase** — *"Make informed defaults for unspecified details"* is the inverse of R9 and R10, which require per-requirement confirmation and an explicit agreement to terminate. **Two earlier grounds are withdrawn**: a hard error on empty input and a three-marker clarification cap are in neither current preset, re-read 2026-09-01 — both are 23 lines, and `NEEDS CLARIFICATION` survives uncapped in `templates/spec-template.md`. The rejection now rests on the defaults clause alone.
- **`create-prd`, `alirezarezvani`'s PRD, `define-problem-statement`** — screened; nothing survives verification beyond R1 and one or two content slots. **Not re-read at component level.** These were rejected as skills, which is the error corrected above; the three lowest pass counts make a find unlikely, not impossible. Open.

## Open questions

**Scope of the artifact-content rules, ruled here because a review found the question live.** R15, R18, R24, R35, R37 and R38 govern the artifact the *skill produces*. **R40 is the exception and is not exempted**: this document's own sections were reordered to satisfy it on 2026-09-01, making it the only artifact rule with a compliant worked instance. They do **not** bind this document, which is an input to building that skill rather than an instance of its output. R4 and R9 were split on merit — a conjunction hides an untested half, and the sourcing screen demonstrated exactly that failure on R4 — not because R15 obliged it. A review that applies R15 to this document while declining to apply R18 to it is inconsistent; the consistent position is that neither applies.

- Do R3 and R29 earn their place? Neither drove a sourcing verdict. R3 is additionally unreviewed. (R24 was on this list and comes off: four candidates claimed it and eight did not — so it discriminated. Verification then refuted at least one of the four, `framing-doc`, which survives on R11 and R13 only.)

- Does R7 do any screening work, or is it describing the field?

- Do constraints belong before the requirements? 12207's activity order puts them first; readability puts them after. Currently after.

- Does each requirement carry its nature — decided, corrected, deferred, measured? Currently only exceptions are marked.

- What is the confirmation token? R10 now requires one chosen in advance and not used conversationally; which token is yours to pick, and it has to be picked before the phase can run.

- **No compliant exemplar of the output exists, and R27 widened the gap.** The scope ruling below exempts this document from R15, R18, R24 and now R35, R37 and R38 — this document's requirements lean on their section headings, its prose carries obligations outside requirement statements, and no set-level consistency check has been run on it. So the only worked instance is exempt from **six** rules the skill must enforce — and the exemption is load-bearing: R2 joins three conditions with "or" against R15, and R19 uses "never" twice against 29148 5.2.7's totality terms. (29148 5.2.8 uses "never" too, which is why the exemption exists and why an exemplar is needed to show what does survive.) Ship a compliant sample artifact, or the skill is built against a specification never instantiated.

- ~~**Is R27 finished on this set?**~~ **Closed 2026-09-01.** All four remaining corpora were read properly; `docs/research/2026-09-01-r27-completion.md` carries the result. The prediction that finishing it would repay itself held: R24's escape hatch and R28's ordering were both confirmed at their primaries, and five requirements were found that no earlier pass had. The collision rule was **not** confirmed — the corpus that would have supplied it was refuted on transfer.

**Closed since drafting.**

*Do R26–R28 belong in a skill screen?* No. They are pipeline requirements; a pipeline is composed rather than sourced, and the universal failure measured the screen's granularity. Moved into the Pipeline section as a statement.

*Is R10 safe against acquiescence?* The disagreement is dissolved rather than adjudicated. Fitzpatrick's objection is to **verbal assent** as a termination signal — an utterance whose politeness meaning is indistinguishable from its agreement meaning. A token chosen in advance and never used conversationally is not that; it cannot be produced by politeness. 12207's process outcome is satisfied and Fitzpatrick's failure mode is closed, without needing his costly-commitment substitute.

## Evidence

Each phase section above links its own research note. Those paths are bare relative paths, deliberately. An earlier version instructed pinning them to a commit against the coming reorganisation; that was wrong for this repo, whose practice is to rewrite links when things move — #90 did exactly that. (#92 is not a witness for it: it swept titles and a retired prefix, and its resolution states "URLs and repo-slug links untouched".) A pinned link survives the move by pointing at a superseded copy, which is worse than a path that breaks loudly and gets fixed.

Primary sources read directly: ISO/IEC/IEEE 29148:2018 (`sources/29148-2018.pdf`, clauses 5.2.5–5.2.8); ISO/IEC/IEEE 12207:2017 (`sources/12207-2017.pdf`, clause 6.4.2); the Volere requirements shell; the bodies of `brainstorming`, `interview-me`, `shape-spec`, `write-spec`, `deliver-prd`, `define-problem-statement`, `requirements-clarity`, `helm-brief`, `framing-doc`, `matter-intake-scoping`, `incoming-request-advisor`, `neuroarxiv`, `adhd`, `to-spec`, `grilling`, `research`, `writing-plans`, `subagent-driven-development`, and spec-kit's `specify.md` and `spec-template.md`.

Evidence ladder applied: standards-body consensus documents rank highest; then regulatory text; then published research; then named practitioner methods; then upstream artifacts read directly; and this project's own working documents lowest — primary about themselves, and evidence about nothing else.
