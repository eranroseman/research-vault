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

## Out of scope

Each item is something a reader would reasonably expect this phase to do.

- **Deciding whether to build.** This phase assumes that decision is made. A funnel with a kill gate is a different tool; for an already-decided need, spec-kit's `assess` cannot reach a `go` verdict at all.
- **Producing a PRD.** Stakeholder sign-off, timelines, milestones, dependencies-with-owners and escalation matrices are the machinery of an organisation, and there is not one here.
- **Aligning multiple stakeholders.** One person holds the need, the decision and the cost. This is why most of the field's apparatus does not transfer, and it is the assumption most likely to become wrong later.
- **Prioritising or sequencing the requirements.** No MoSCoW, no P1/P2/P3. This artifact holds only musts; ISO/IEC/IEEE 12207:2017 puts the down-select on *needs*, one step upstream.
- **Traceability past handoff.** 29148 and the regulated regimes trace a requirement through to verification and code. This stops when `writing-specs` takes the artifact.
- **Running non-interactively.** A live dialogue by definition. What it does instead is R33, not a scope note — an earlier version smuggled testable behaviour into this list with no number, no source and no fit.

## Requirements

Source vocabulary, defined by **origin** rather than by confirmation status: `elicited` — stated directly, quoted where short. `inferred` — derived from what was stated. `assumed` — brought from the agent's general knowledge rather than from anything said. Otherwise a named document. Any of the three may be confirmed or not; confirmation is tracked separately, because defining a class by confirmation status leaves agent-supplied-and-confirmed material with no label — which is what R12's three classes and R23 both need.

### Skill behaviour

**R1** — Accepts a need arriving unframed in conversation.
*Fit:* a bare sentence with no user, no success criterion and no constraint produces a first turn, not an error.
*Source:* `elicited` — "the usual route is chat → spec → plan".

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
*Source:* `elicited` — "I prefer agents interviewing me all day long if that is what is needed to get the job right." Null result: no practice surveyed caps question count.
*Note:* drove no rejection in the sourcing screen except jointly with R1. May be describing the field rather than screening it.

**R8** — Writes each requirement as its answer settles, not in one pass at the end.
*Fit:* a requirement exists in the artifact before the interview ends.
*Source:* `elicited` — "interview user for why and what, write requirement, verify, repeat until done."

**R9** — Confirms each requirement when it is written.
*Fit:* no requirement enters the artifact unconfirmed.
*Source:* contextual inquiry's *Interpretation* principle; qualitative research's *member checking*. Both are continuous rather than terminal. `assumed` — the rendering is mine.

**R31** — Restates the accumulated set before terminating.
*Fit:* the final restate covers every requirement written, not only those settled last.
*Source:* as R9. Split out from it — continuous confirmation and a terminal restate are two obligations, and a skill could satisfy either alone.

**R10** — Terminates on a confirmation signal I chose in advance and do not use conversationally.
*Fit:* the signal is agreed before the phase runs and is distinguishable from assent — "sounds good", "sure", "looks right" and silence do not match it. No score and no count substitutes for it.
*Source:* ISO/IEC/IEEE 12207:2017 6.4.2.2(g) — "Stakeholder agreement that their needs and expectations are reflected adequately in the requirements is achieved." `assumed` — adopting it here is unconfirmed. The prohibition on an LLM-judged score as the gate is a decision, not evidence; no standard has a position on it.

### Artifact content

**R3** — Records which workload and risk class the need belongs to, with the reason.
*Fit:* the artifact states the class; a reader can tell a coaching-app feature from a tooling decision without reading further.
*Source:* `assumed` — four regulatory regimes scale rigour by a declared tier and make the declaration a deliverable that never scales down. Not yet reviewed, and it drove no sourcing verdict.

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

**R21** — Records what is excluded.
*Fit:* at least one item a reasonable reader would assume is in scope.
*Source:* `interview-me`, `shape-spec` and `helm-brief` independently.

**R22** — Records constraints that bind this need, including sourcing decisions already binding.
*Fit:* each is falsifiable.
*Source:* 12207:2017 6.4.2.3(d.1) — constraints include "required use of defined enabling, legacy, or interfacing systems" and "unavoidable consequences of existing agreements".

**R23** — Generates requirements from abuse and failure scenarios, not only from stated needs.
*Fit:* the artifact contains at least one requirement nobody asked for.
*Source:* 12207:2017 6.4.2.3(c.1) — "Abuse and failure scenarios highlight the need for additional functional requirements."

**R24** — Contains no architecture, components, phases or estimates.
*Fit:* nothing in the **requirement list** would change if the implementation approach changed. Scoped to the requirements rather than the whole artifact: R28 puts sourcing verdicts in their own section, and those are approach decisions by definition. Both traditions draw the line the same way — sourcing belongs in the document, not in a requirement.
*Source:* 29148:2018 5.2.7 — "Requirements should state 'what' is needed, not 'how'." A `should`, with an acknowledged exception at lower decomposition levels.
*Note:* it did screen. Four of twelve candidates claimed it — `interview-me`, `shape-spec`, spec-kit `/specify`, `framing-doc` — and eight failed. An earlier note here claimed the opposite and was false against the screen's own table.

**R25** — Records open questions, exempt from the completeness count.
*Fit:* an artifact with open questions can still be confirmed.
*Source:* 29148:2018 5.2.6 permits TBx during evolution — "Resolution of the TBx designations may be iterative and there is an acceptable timeframe for TBx items" — and forbids them at completion. The exemption holds because this artifact is never the completed set: it is an input to a design phase that resolves the open items, and it is archived rather than contracted.

**R33** — In a non-interactive context, names the questions it would have asked and stops, rather than answering them itself.
*Fit:* a run with no user produces a question list and no requirements.
*Source:* `elicited`, as a scope note; numbered here because it is behaviour, not scope. The subagent run of 2026-09-01 is the worked example — and it detected the absent user because it was told, not because anything in this design would have.

**R32** — Records whether the confirmation gate has passed.
*Fit:* a cold session opening the file can tell a confirmed artifact from an abandoned one without asking.
*Source:* `inferred` — follows from R8, R10 and R29 interacting. R8 guarantees a partial artifact exists on disk mid-interview; R29 promises cold-session consumption at a stable path; R10 defines a gate whose outcome nothing currently records. Without this, `writing-specs` cannot distinguish a set I confirmed from one I walked away from.

### Pipeline

These three are requirements on the **phase**, not on any single skill. Every candidate failed all three — which measures the granularity of the screen, not a gap in the field. A skill does not contain three sub-steps that are themselves skills; a pipeline composes them. They are satisfied by the composition and are not screening criteria for any component of it.

**Delivery, ruled 2026-09-01: one skill with three internally-gated phases**, each dispatching an isolated subagent. Three named sub-skills would put three descriptions with exactly one caller each into the router's match pool — the same failure `grilling`'s description suppression was fighting. Delegating to the installed `research` skill fails R26's fit, which requires patterns to arrive already shaped as requirements rather than as candidates to weigh. The one real cost — phases not independently re-runnable — is met by an optional entry argument naming a phase, so re-running sourcing alone does not mean re-entering the loop.

**R26** — Runs a prior-art step before writing requirements, behind a gate.
*Fit:* patterns found arrive as requirements, not as candidates to weigh.
*Source:* `elicited` — the sequence. The cost of skipping it was paid in this session.

**R27** — Runs a competitive-analysis step that edits the requirement set before the confirm gate.
*Fit:* its output is edits to requirements — added, recalibrated, dropped, confirmed — not verdicts on competitors.
*Source:* `elicited` — "how my requirements compare to other solutions."

**R28** — Runs a sourcing step after requirements settle, whose verdicts land in their own section rather than as requirements.
*Fit:* a reader can tell which came first.
*Source:* 29148:2018 5.2.5 NOTE 1 names "a system that can be bought rather than made" as an inappropriate requirement; Volere places Off-the-Shelf Solutions at section 19, separate from Functional Requirements at 9.

### Integration

**R29** — Output lands at a stable path with a header naming its consumer.
*Fit:* `/writing-specs @path` works from a cold session.
*Source:* the house convention, specified verbatim in `writing-plans`' plan header.
*Note:* every candidate failed it, so it screened nothing — the same shape as R26–R28. An obligation on what we build, not a discriminator among what we might take.

## Constraints

- Runs on Claude Code and Codex.
- Sourced rather than authored where possible; fewest changes.
- Archived on handoff, never maintained. Drift from the product is expected.
- `writing-specs` is the only consumer, and it is not modified by this phase.
- **Enumerability is a pipeline obligation, and it is not discharged here.** `writing-plans` never reads this artifact — its Self-Review walks the *spec* against the *plan*: "Can you point to a task that implements it? List any gaps." So each requirement must survive into the spec in a form that check can walk. **Nothing in this phase can guarantee that**, because the guarantee belongs to `writing-specs`' own design, which #60 and #62 own. Filed there as an obligation, not left here as an aside. (An earlier version claimed `writing-plans` consumes this artifact directly; it does not.)
- MIT and Apache-2.0 attribution is owed wherever text is taken substantially, regardless of how the maintenance relationship is described.

## Sourcing decisions

Sourcing sits in this phase because `writing-specs` cannot hold it — its approach comparison is architectural alternatives inside your own tree, not build-or-buy. **Trigger to move: `writing-specs` gains build-or-buy comparison.**

**Screen result, 2026-09-01.** Twelve candidates screened pass/fail against the twenty-nine requirements that existed at the time, one isolated agent each, every result adversarially verified. **R30, R31 and R32 post-date the screen and no candidate has been tested against them.** R30 exists to preserve a measured failure: the screen failed `interview-me` on the batching half of the old R4, and the narrowed R4's fit would no longer record it. No candidate ever passed R4 — it appears in no pass column — so nothing was flipped by the split. Claimed passes ran three to eight; after verification **nothing exceeds three of twenty-nine**.

That measurement closes the top three treatments for anything taken **for its content** — **install a plugin as-is**, **fork it and keep merging**, **copy it frozen** — since each takes something failing at least twenty-six musts.

What remains is **copy plus a delta**, **author to someone else's design and credit it**, or **write from scratch**. (The first five are the sourcing ladder drafted in `docs/2026-08-31-proposed-adr-software-development-component-adoption.md`, which is a proposal and not accepted. The sixth — author to someone else's design and credit it — is **not in that draft**; it was added in the 2026-09-01 conversation, along with a ruling that the ladder is not finalised. Names used for brevity, not as authority.)

### Adapt

| Source                                           | Licence    | What we take                                                                                                                                                                         | Why                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ------------------------------------------------ | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `write-spec` — anthropics/knowledge-work-plugins | Apache-2.0 | The per-requirement acceptance-criteria discipline — "Requirements: Categorized as Must-Have (P0), Nice-to-Have (P1), and Future Considerations (P2), each with acceptance criteria" | The only candidate passing R14 after verification. Rename to avoid the collision with `writing-specs`; strip the connector placeholders                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `deliver-prd` — product-on-purpose/pm-skills     | Apache-2.0 | The Requirement Verification Map, the AI Behavior and Evaluation section, and the conditional-section discipline                                                                     | The only source with model-behaviour requirements tied to evidence — needed for the coaching-app workload                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `interview-me` — addyosmani/agent-skills         | MIT        | The explicit-yes gate with its enumerated false yeses, and the confidence-number-with-a-reason                                                                                       | The only termination condition available that is neither a score nor a count. **Its loop is not taken**: it fails R30, R5, R8 and R9 — one question at a time, a single guess, nothing written until the end, and no per-requirement confirmation. It does satisfy R31, the terminal restate                                                                                                                                                                                                                                                                                   |
| `brainstorming` — obra/superpowers               | MIT        | The shape of a process skill: a hard gate, a numbered checklist, a one-way ratchet, an anti-pattern table, a named handoff ritual                                                    | Read at **v6.2.0**, the version installed on both harnesses. Four deltas: the classifier is dropped — Spike/Bounded/Architectural classifies code, and "bounded" is defined by whether the flow already exists in the repo, which a need has no equivalent of; the write moves to the top of the loop per R8; the anti-pattern rows are rewritten because upstream's argue against R2's decline; the ratchet is retargeted, so a started run never downgrades to a decline. That last idea comes from v6.3.0's path system — 6.2.0 has no paths and nothing to ratchet between |

### Take the idea — credited, not copied

| Source                               | What we take                                                                                                           | Serves                                                  |
| ------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| Volere requirements shell            | Description, Originator, Fit Criterion                                                                                 | R11, R14                                                |
| ISO/IEC/IEEE 29148:2018              | 5.2.5 characteristics; 5.2.7 forbidden terms; 5.2.8 identifier rule                                                    | R15, R18, R19                                           |
| ISO/IEC/IEEE 12207:2017              | Agreement as a process outcome; abuse-and-failure scenarios; the four constraint sources                               | R10, R23, R22                                           |
| Planguage — Gilb                     | Scale and meter; `Must` versus `Plan`                                                                                  | R16, R17                                                |
| `shape-spec` — duthaho/claudekit     | "Ceremony is what scales, not the gate", and evidence never scaling to zero                                            | The invariant `brainstorming` implements without naming |
| `neuroarxiv` / `adhd` — UditAkhourii | The three-question pre-flight with explicit-invocation bypass; the isolation invariant; converge rather than shortlist | R2, R26's gate                                          |
| `framing-doc` — rjs/shaping-skills   | The per-line provenance audit with a delete rule. **No LICENSE file — idea only**                                      | R11, R13 (the only two it passes)                       |
| Fitzpatrick, *The Mom Test*          | Anchor in specific past events; verbatim marked as verbatim                                                            | R6, R13                                                 |
| Willis; Pew Research                 | Multi-possibility probing over single-possibility                                                                      | R5                                                      |

### Defer

- **`spec-kit`** — trigger: it stabilises, or the phase needs a machine-checkable gate. Its v1.0.0 release notes disavow their own compatibility promise.
- **`helm-brief`, `matter-intake-scoping`, `incoming-request-advisor`** — their labelled-inference schemes overlap what Volere and 29148 already supply. Trigger: R12's three classes prove insufficient in use.

### Reject

- **`requirements-clarity`** — its gate is an LLM-judged 90/100 score, and 50 of its 100 rubric points are the how.
- **spec-kit `/specify` as the phase** — hard-errors on empty input; caps clarification at three markers.
- **`create-prd`, `alirezarezvani`'s PRD, `define-problem-statement`** — screened; nothing survives verification beyond R1 and one or two content slots.

## Open questions

**Scope of the artifact-content rules, ruled here because a review found the question live.** R15, R18 and R24 govern the artifact the *skill produces*. They do **not** bind this document, which is an input to building that skill rather than an instance of its output. R4 and R9 were split on merit — a conjunction hides an untested half, and the sourcing screen demonstrated exactly that failure on R4 — not because R15 obliged it. A review that applies R15 to this document while declining to apply R18 to it is inconsistent; the consistent position is that neither applies.

- Do R3 and R29 earn their place? Neither drove a sourcing verdict. R3 is additionally unreviewed. (R24 was on this list and comes off: four candidates claimed it and eight did not — so it discriminated. Verification then refuted at least one of the four, `framing-doc`, which survives on R11 and R13 only.)

- Does R7 do any screening work, or is it describing the field?

- Do constraints belong before the requirements? 12207's activity order puts them first; readability puts them after. Currently after.

- Does each requirement carry its nature — decided, corrected, deferred, measured? Currently only exceptions are marked.

- What is the confirmation token? R10 now requires one chosen in advance and not used conversationally; which token is yours to pick, and it has to be picked before the phase can run.

- **No compliant exemplar of the output exists.** The scope ruling below exempts this document from R15, R18 and R24, so the only worked instance is exempt from three rules the skill must enforce — and the exemption is load-bearing: R2 joins three conditions with "or" against R15, and R19 uses "never" twice against 29148 5.2.7's totality terms. (29148 5.2.8 uses "never" too, which is why the exemption exists and why an exemplar is needed to show what does survive.) Ship a compliant sample artifact, or the skill is built against a specification never instantiated.

- **Is R27 finished on this set?** No. Four of six corpora were read as headlines and remain leads. Their unapplied items predicted at least three defects found later by review — the collision rule, R24's missing escape hatch, and R28's ordering. Finishing it before building buys defect-detection already paid for.

**Closed since drafting.**

*Do R26–R28 belong in a skill screen?* No. They are pipeline requirements; a pipeline is composed rather than sourced, and the universal failure measured the screen's granularity. Moved into the Pipeline section as a statement.

*Is R10 safe against acquiescence?* The disagreement is dissolved rather than adjudicated. Fitzpatrick's objection is to **verbal assent** as a termination signal — an utterance whose politeness meaning is indistinguishable from its agreement meaning. A token chosen in advance and never used conversationally is not that; it cannot be produced by politeness. 12207's process outcome is satisfied and Fitzpatrick's failure mode is closed, without needing his costly-commitment substitute.

## Evidence

- **Prior art** — `docs/research/2026-09-01-requirements-artifact-prior-art.md`
- **Competitive analysis** — `docs/research/2026-09-01-pre-spec-competitive-analysis.md`. **Carries unapplied findings**: four of its six corpora were read as verdict headlines only, and their items are leads rather than findings.
- **Sourcing screen** — `docs/research/2026-09-01-pre-spec-sourcing-screen.md`

Bare relative paths, deliberately. An earlier version instructed pinning them to a commit against the coming reorganisation; that was wrong for this repo, whose practice is to rewrite links when things move — #90 did exactly that. (#92 is not a witness for it: it swept titles and a retired prefix, and its resolution states "URLs and repo-slug links untouched".) A pinned link survives the move by pointing at a superseded copy, which is worse than a path that breaks loudly and gets fixed.

Primary sources read directly: ISO/IEC/IEEE 29148:2018 (`sources/29148-2018.pdf`, clauses 5.2.5–5.2.8); ISO/IEC/IEEE 12207:2017 (`sources/12207-2017.pdf`, clause 6.4.2); the Volere requirements shell; the bodies of `brainstorming`, `interview-me`, `shape-spec`, `write-spec`, `deliver-prd`, `define-problem-statement`, `requirements-clarity`, `helm-brief`, `framing-doc`, `matter-intake-scoping`, `incoming-request-advisor`, `neuroarxiv`, `adhd`, `to-spec`, `grilling`, `research`, `writing-plans`, `subagent-driven-development`, and spec-kit's `specify.md` and `spec-template.md`.

Evidence ladder applied: standards-body consensus documents rank highest; then regulatory text; then published research; then named practitioner methods; then upstream artifacts read directly; and this project's own working documents lowest — primary about themselves, and evidence about nothing else.
