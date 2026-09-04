# Requirements: writing-reqs (the pre-spec phase)

> **For agentic workers:** this document is the input to a design or a sourcing phase, not a design. On approval it offers two successors — `sourcing` (is there anything we can use?) or `writing-specs` (how do we build it?) — and neither is a default.
>
> **Status:** **feature-complete, 2026-09-02.** 39 requirements, six retired numbers (R3, R10, R16, R17, R28, R31). Eight are hard floors under R43. Every requirement derives from prior art or a screened competitor, every source has been read directly, and every requirement has a named consumer. A red-team pass confirmed three blockers and thirteen minor defects; all sixteen are fixed. Six independent attacks on the joint satisfiability of R15, R18, R24, R35, R37 and R38 were all refuted, which was the one question that could have blocked this.
>
> **Not confirmed, and deliberately so.** R42 requires me to read this file and answer with a signal distinguishable from assent, and R32 forbids recording a set as confirmed while any requirement in it is unconfirmed. Neither has happened. Marking this confirmed to tidy the status line is precisely the hollow confirmation the red team found and R42 now forbids — so the artifact that specifies the gate is the first thing held by it. Sourcing may be re-run against this set; the set is not agreed until the gate runs.
>
> Identifiers are never changed and never reused, which is why splitting R4 and R9 produced R30 and R31 rather than renumbering, and why the retired six leave gaps. R31 was itself later retired, superseded by R42.
>
> **Delete when** `writing-reqs` ships and its skill body carries these requirements, or when the design is abandoned. This document is scaffolding, not a record: git history holds it after deletion. Precedent — `553ae6f`, "delete 14 merged/abandoned superpowers plan files". A never-maintained file sitting at a stable path is the stale record that deletion exists to prevent.
>
> **Sequencing, ruled 2026-09-01:** build now, not after `writing-specs`. `writing-reqs` is written here, drawing text from four skills rather than vendored from any one — so it never merges upstream, was never a drift surface, and waiting for `writing-specs` buys nothing. The two are not siblings and are not required to match; each carries what its own altitude needs. **The R27 gate is lifted, 2026-09-01** — all six corpora are read and applied; `docs/research/2026-09-01-r27-completion.md` carries the result. Nothing now blocks building.
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

| Source                                      | What it gave                                                                                                                                                                                | Requirements                                                |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| ISO/IEC/IEEE 29148:2018                     | 5.2.5 characteristics; 5.2.6 TBx; 5.2.7 forbidden terms and the no-how rule; 5.2.8 identifiers                                                                                              | R15, R18, R19, R24, R25, R28                                |
| ISO/IEC/IEEE 12207:2017                     | 6.4.2.2(g) agreement as an outcome; 6.4.2.3(c.1) abuse and failure; (d.1) constraint sources                                                                                                | R22, R23                                                    |
| ECSS-E-ST-10-06C                            | 5.2 the two-baseline process and the low-heritage gate; 7.2.3d consistency; 7.2.7a informative clauses carry no requirement; 8.2.8a self-contained; Annex A the normative table of contents | R26, R27, R29, R35, R37, R38, R40                           |
| FAR Parts 10, 11, 16                        | 10.001(a)(2)(i) research before requirements; 10.002(a) the entry condition; 10.002(c) re-evaluate the need; 11.105 "or equivalent"; 16.603-2(c) a deadline on the unresolved               | R1, R24, R25, R26, R28                                      |
| FAA REMH DOT/FAA/AR-08/32                   | §2.4 environmental assumptions; §2.8.4 one ideal value per variable; §2.11.7 capture rationale as you go                                                                                    | R8, R36, R37                                                |
| INCOSE GtWR V3.1                            | *INCOSE R25* on headings; the five set-level characteristics                                                                                                                                | R35                                                         |
| Volere requirements shell                   | Description, Originator, Fit Criterion                                                                                                                                                      | R11, R14                                                    |
| Gilb, *Competitive Engineering*             | The Meter — naming how a thing is measured, not only what                                                                                                                                   | R14                                                         |
| Fitzpatrick, *The Mom Test*                 | Specifics in the past, not generics or opinions; exact quotes wrapped as verbatim                                                                                                           | R6, R13                                                     |
| Willis (1999 and 2012); Pew Research Center | List all reasonable possibilities rather than suggesting one                                                                                                                                | R5                                                          |
| Beyer and Holtzblatt, *Contextual Design*   | The Interpretation principle — an interpretation is validated by sharing it                                                                                                                 | R9                                                          |
| NIST AI 100-1                               | Go/no-go as a named process outcome                                                                                                                                                         | R32                                                         |
| IMDRF SaMD N10, N12, N41                    | Medical purpose as the gate; the I–IV matrix; categorization relies on the definition statement                                                                                             | *none — R3 retired.* Kept for #100, which owns the boundary |
| IEEE adoption of ISO/IEC 15026-3            | Risk analysis before the first integrity-level assignment                                                                                                                                   | *none — R3 retired.* Kept for #100                          |
| OpenAI Model Spec 2026-08-18                | Overridable authority levels; name the missing artifact rather than supplying it                                                                                                            | R33, R39                                                    |
| Anthropic Usage Policy                      | High-Risk use cases; human-in-the-loop; the wellness carve-out                                                                                                                              | R41                                                         |
| PCR 2015 reg 42(13)                         | Naming a specific make "on an exceptional basis", with "or equivalent"                                                                                                                      | R24                                                         |

Identifiers in the middle column belong to the source document, not to this one — *INCOSE R25* is INCOSE's rule, not this set's open-questions requirement. Two rows now generate nothing, their requirement having been retired; they are kept because #100 owns the question they bear on. None of these is a sourcing decision. The rest generated requirements; they are not components and nothing is bought from them. The sourcing section below holds only skills and skill components.

**One requirement has no anchor here.** The phase's own success criterion is stated by no tradition surveyed — named rather than stretched onto a near-miss.

## Competitive analysis

Six corpora. It ran **after** the requirements were drafted and edited them, and is presented **before** them because the set below is the post-update one — several requirements exist only because this pass found them, and reading them first would leave those unexplained.

**What it changed.** The largest correction was to the interview loop. A guess attached to an open question is a mutation of a technique that is backward-looking in both traditions that use it, and the harm is measured rather than argued: acquiescence bias, worse with an interviewer present. Anchoring questions in specific past events entered as the most-agreed rule in the discovery corpus. Which requirement each finding produced is on that requirement's *Source* line.

**The disagreement it left open.** Fitzpatrick holds that verbal assent is exactly the data type that must not terminate elicitation; ISO/IEC/IEEE 12207 6.4.2.2(g) makes stakeholder agreement a process outcome. This set took the standards position. R42 later dissolved the conflict rather than settling it, by moving the agreement out of conversation and onto a committed file — reading a document is not verbal assent.

**Limits.** Four of the six corpora were first read as headlines only and completed on 2026-09-01. That second pass refuted more than it confirmed, and two of its claims did not survive: the three procurement regimes cited for R24's escape hatch are **not independent**, all descending from WTO GPA Article X; and a predicted two-tier gap was **not established**, its corpus refuted on transfer and its surviving finding resting on a goals section this document does not have.

## Requirements

**Field order:** statement, *Fit*, *Why* (R44), *Floor* and *Version* on one line (R43, R45), *Source* (R11). **Eight requirements are hard floors** — R1, R8, R9, R11, R14, R20, R24, R42 — marked by the author on 2026-09-02 against the test *would I abandon the need rather than give this up?* The other thirty-one are marked no. `sourcing` S19 searches on these eight and on nothing else; it does not screen, since screening is the design phase's.

**Retired numbers: R3, R10, R16, R17, R28, R31.** R31 was the terminal restate, split out of R9 when the terminal act was a restatement in conversation. R42 later replaced that act with reading the committed file, which is the same assessment of a stronger artifact — so R31 became the weaker half of a doubled review and was dropped on 2026-09-02. R9's per-requirement confirmation has no such overlap and stands. All dropped on 2026-09-02 under the test *"if dropped, does it hurt functionality or remove needless ceremony?"* — none had a consumer — **except R10, and that claim was false when written**: old R32's source line named it, "R10 defines a gate whose outcome nothing currently records". R10's function is superseded by R42, which reaches the same end by asking for changes rather than by agreeing a token in advance. R16's measurement-method clause survives inside R14. R34 is now issued; R41 is a split from R22. **R28 is retired for a different reason** — not ceremony, but relocation: sourcing became a separate skill on 2026-09-02, so its requirement belongs to that skill rather than to this one. Identifiers are never reused (R19), so the gaps are deliberate.

Source vocabulary, defined by **origin** rather than by confirmation status: `elicited` — stated directly, quoted where short. `inferred` — derived from what was stated. `assumed` — brought from the agent's general knowledge rather than from anything said. Otherwise a named document. Any of the three may be confirmed or not; confirmation is tracked separately, because defining a class by confirmation status leaves agent-supplied-and-confirmed material with no label — which is what R12's three classes and R23 both need.

### Skill behaviour

**R1** — Accepts a need arriving unframed in conversation.
*Fit:* a bare sentence with no user, no success criterion and no constraint produces a **question**, not an error and not a decline. A run that declines every unframed need passes nothing here.
*Why:* Requiring the need be framed before the phase starts would make the author do the phase's work before invoking it. Unframed arrival is the entry state this skill exists for.
*Floor:* **yes** · *Version:* 1
*Source:* FAR 10.002(a), FAC 2026-01 — "Acquisitions begin with a description of the Government's needs stated in terms sufficient to allow conduct of market research." A rough description is the legitimate entry state, not a defect. Verified locally 2026-09-01. Previously `elicited` — "the usual route is chat → spec → plan" — which is still the origin, now with a primary behind it.

**R2** — Declines when no real question remains, the work is small, or the approach is already chosen.
*Fit:* the run checks three conditions — a real question remains open, the work exceeds a quick change, the approach is still undecided. Any condition that fails ends the run in one sentence naming how to invoke the skill deliberately.
*Why:* An interview run when the answer is already known spends the attention this skill exists to conserve, and produces an artifact nobody reads.
*Floor:* no · *Version:* 1
*Source:* `neuroarxiv` and `adhd` pre-flight gates, both with an explicit-invocation bypass.

**R4** — Asks questions in dependency order.
*Fit:* no question is asked whose answer hinges on another still open in the same round. **A round is one agent turn carrying at least one question, plus my reply to it** — the definition R8 and R30 use.
*Why:* A question whose answer depends on an open one gets answered speculatively, and the speculation is then recorded as settled.
*Floor:* no · *Version:* 1
*Source:* `mattpocock/skills` commit `a4b2009a` — "Same 13 questions land in ~3 rounds instead of 13."

**R30** — Asks mutually independent questions in one round.
*Fit:* in every round, each question whose answer does not hinge on another open question is asked in that round rather than held for the next. A run that asks one question per round, ever, fails.
*Why:* Serialising independent questions multiplies round-trips without adding information, and the cost lands on the author's attention.
*Floor:* no · *Version:* 1
*Source:* as R4. Split out because the two were joined by a conjunction and only the first was tested — the sourcing screen failed `interview-me` on the second half while R4's written fit would have passed it.

**R5** — Offers the plausible alternatives, never a single guess, when it proposes an answer before the user gives one.
*Fit:* every question that proposes answers offers two or more, records where each came from — prior art, a screened competitor, or the transcript — and leaves an answer outside the list available. A reviewer can then ask what a named source offered that the question omitted, which the run cannot answer for itself.
*Why:* A single attached guess makes agreement cheaper than correction, and the failure is invisible: an agreeable answer looks identical to a correct one.
*Floor:* no · *Version:* 1
*Source:* Willis, *Cognitive Interviewing: A "How To" Guide* (1999, Research Triangle Institute / ASA short course) **and** *Cognitive Interviewing Training Guide* (2012), **both read directly 2026-09-01**, carrying the passage **identically thirteen years apart** — "rather than suggesting to the subject one possibility ('Did you think the question was asking just about physicians?'), it is preferable to list all reasonable possibilities… probes should be characterized by unbiased phrasing". **Correction:** the labels "single-possibility" and "multi-possibility probing" appear **nowhere** in either guide, nor in a published review of the 2005 book. Searched in three documents, zero hits. They were reported as quotation and are not. The substance is verbatim, the terminology is not from this source. Pew Research Center, *Writing Survey Questions* (methods section, `pewresearch.org/writing-survey-questions/`), **read directly 2026-09-01** — "This is sometimes called an 'acquiescence bias'… This behavior is even more pronounced **when there's an interviewer present**, rather than when the survey is self-administered. **A better practice is to offer respondents a choice between alternative statements.**" Pew independently supplies the *remedy*, not merely the harm, so R5 has two legs that converge.

**R6** — Anchors questions about the problem in specific past events, not in opinions, generalities or predictions.
*Fit:* every question about the need, its cost and the current workaround asks what happened. Only questions about the wanted outcome ask about the future, and the artifact records their answers as goals rather than as evidence.
*Why:* What someone predicts they will do is not evidence about what they do. A requirement built on a prediction cannot be shown wrong until the software ships.
*Floor:* no · *Version:* 1
*Source:* Fitzpatrick, *The Mom Test*, **read directly 2026-09-01**, rule 2 of three: "Talk about their life instead of your idea. **Ask about specifics in the past instead of generics or opinions about the future.** Talk less and listen more." Verbatim, and the requirement is a restatement of it. The competitive analysis additionally claimed convergence across "three independent primaries"; **two were never named and remain unrecovered**, so the convergence claim stays unverified even though the requirement no longer depends on it.

**R7** — Places no cap on the number of questions.
*Fit:* no number anywhere in the skill limits how many questions it asks or how many open questions (R25) the artifact holds. Questioning ends at the review gate (R42), not at a count and not because the run judges its own understanding sufficient. Two other terminations are permitted and named: R2's decline at entry, and R33's stop when there is no user to ask.
*Why:* Any cap stops the skill before understanding is reached. It optimises for the agent's convenience against the artifact's correctness.
*Floor:* no · *Version:* 1
*Source:* a **null result** from the competitive-analysis pass, which is evidence rather than an absence of it: no practice surveyed caps question count, and every one caps something adjacent instead — learning goals per person-type, session length, question density. Searching 29148 and 12207 for any cap on elicitation effort returned nothing, consistent with that. Competitive-analysis derived, not prior art; no prior art exists to derive it from. The author's position — "I prefer agents interviewing me all day long if that is what is needed to get the job right" — is the origin.
*Note:* drove no rejection in the sourcing screen except jointly with R1. May be describing the field rather than screening it.

**R8** — Writes each requirement in the round its answer settles.
*Fit:* at the end of every round, the artifact holds a requirement for each answer that round settled. A run that reaches the review gate with requirements written after the last question fails.
*Why:* Writing at the end records the agent's memory of the conversation rather than the conversation. Answers settle and then drift.
*Floor:* **yes** · *Version:* 1
*Source:* FAA REMH DOT/FAA/AR-08/32 §2.11.7, verified locally 2026-09-01 — "Rationale should be collected along with the development of the requirement… This ensures that the justification is captured by the author while he or she is thinking about it… it is much simpler to record the rationale when the latency was being computed than to try to re-engineer the reasoning later." The reason given is the author's attention, which is this requirement's reason too. Origin: `elicited` — "interview user for why and what, write requirement, verify, repeat until done."

**R9** — Restates each requirement to me when it is written, and records whether I confirmed it.
*Fit:* every requirement in the artifact carries a confirmation status. A requirement I have not confirmed is marked as such and reaches the review gate (R42) still marked.
*Why:* Confirmation gathered once at the end cannot say which part was agreed. A per-requirement status is what distinguishes a settled requirement from an unchallenged one.
*Floor:* **yes** · *Version:* 1
*Source:* Beyer and Holtzblatt, *Contextual Design*, the **Interpretation** principle, **read directly 2026-09-01** — "If the data that matters is the interpretation, we must have a way to ensure it is correct, and we can only do that by **sharing it with the customer**. We fail in the entire purpose of working with customers if we do not share and validate our interpretations of their work." Sharing is continuous and per-interpretation, not terminal, which is what R9 requires, with R42's file review completing it at the end. Qualitative research's *member checking* is the second tradition, still not read directly. The rendering into a per-requirement obligation remains mine.

**R37** — Before the review gate (R42), checks the accumulated requirements as a set.
*Fit:* the sweep reports four results. (1) Conflicts: for each pair sharing a subject, whether their conditions can hold at once, and where they can, that their outcomes agree. (2) Duplicates: no obligation appears twice. (3) Terminology: each term carries one meaning throughout, and every term a requirement refers to is defined by a requirement in the set. (4) Non-singular statements: each requirement states one obligation, which R15 governs per item and only a whole-set pass reliably catches. A collision the sweep finds is resolved, or recorded under R25, before the restate.
*Why:* Per-item review misses set-level defects. R4 and R9 each hid an untested half here until a sourcing screen caught one by accident.
*Floor:* no · *Version:* 1
*Source:* R27, survived verification. ECSS-E-ST-10-06C 7.2.3d — "The technical requirements shall be consistent (e.g. not in conflict with the other requirements within the specification)" — with FAA REMH 2.8.4 giving the operable form, "only one ideal value is assigned to each controlled variable and each internal variable for every possible system state", and INCOSE C11 adding terminology homogeneity. Every rule in the set to this point governs a requirement in isolation; nothing governed the set. The non-singular sweep is ISO/IEC/IEEE 24748-2:2024's — "The resulting set of technical requirements should be checked for non-singular requirements containing multiple parts, which should then be decomposed into individual (singular) requirements" — added because this document hit that defect **twice**: R4 and R9 were each a conjunction with an untested half, split into R30 and R31 only after the sourcing screen caught one by accident. A standard treats it as routine.

**R34** — Runs on Claude Code and Codex.
*Fit:* the skill body invokes only mechanisms both harnesses provide, and a fresh install on each harness produces one complete artifact from one run.
*Why:* A skill that works on one harness fails silently on the other. #56 recorded 8,873 bytes of guidance arriving absent with no error.
*Floor:* no · *Version:* 1
*Source:* the author's ruling of 2026-09-02, promoting it from a constraint on the 29148 3.1.7 test — the harnesses are pre-existing, but supporting both could have been decided otherwise, so it is a requirement. The failure it prevents has already occurred here: #56 records Codex dropping a tracked symlink, so 8,873 bytes of plugin-level `AGENTS.md` guidance arrived silently absent. "From a fresh install" is what catches packaging failures that a body-only check misses.

**R42** — Writes the artifact, then asks me what I want changed before handing off.
*Fit:* the run stops after the artifact is written and committed, names its path, and asks **what I want changed** — not whether I approve. It does not invoke `writing-specs` until I answer, records my answer in the artifact, and treats any requested change as a return to the loop, re-running R37's sweep before asking again. Four runs fail: one that hands off without the pause; one that asks while the artifact is still only in the conversation; one that asks for approval rather than for changes; and one that proceeds on an answer requesting changes. On approval the run names both successors and asks which, recommending neither — the choice depends on the need, not on the artifact.
*Why:* Agreement given in conversation is cheap; agreement given after reading a file is not. Without this the artifact is approved by someone who has not seen it.
*Floor:* **yes** · *Version:* 1
*Source:* `brainstorming` v6.2.0's User Review Gate, verbatim — "Spec written and committed to `<path>`. Please review it and let me know if you want to make any changes before we start writing out the implementation plan." and "Wait for the user's response. If they request changes, make them and re-run the spec review loop. Only proceed once the user approves."
**The question's form is the mechanism.** A question about *changes* cannot be answered by "sounds good" in a way that carries information; a question about *approval* can. That is how `brainstorming` gets a non-assent answer without any pre-agreed token, and why the retired R10 was solving a problem this form dissolves. An earlier version of R42 gated only on a pause — "until I answer" — which a red-team pass broke on 2026-09-02, since every false yes satisfied it; a second version imported R10's token clause, which this replaces on the author's ruling that `brainstorming` is the source.

### Artifact content

**R11** — Each requirement names where it came from.
*Fit:* every requirement carries an origin a reader can check — a passage of the transcript or a named document.
*Why:* A requirement whose origin is unknown cannot be re-decided when circumstances change, and cannot be told apart from something the agent invented.
*Floor:* **yes** · *Version:* 1
*Source:* Volere requirements shell, `Originator`; 12207:2017 6.4.2.2(i).

**R12** — Distinguishes what I said, what the agent inferred from what I said, and what the agent brought from general knowledge.
*Fit:* for each requirement, a reader can say which of the three it is.
*Why:* Agent-supplied material is not wrong, but it is not the author's. A reader who cannot tell the difference cannot audit the set.
*Floor:* no · *Version:* 1
*Source:* `matter-intake-scoping`'s four-level provenance scheme. 12207 treats implicit needs from domain knowledge as a legitimate input, so this marks rather than forbids.

**R13** — Marks quoted material as verbatim, distinct from paraphrase.
*Fit:* quotation marks enclose only words the source used, whether the source is me or a document, and a reader can tell a quotation from the agent's summary of it.
*Why:* A paraphrase presented as a quotation is how a false claim enters wearing the appearance of evidence. This project produced one — a Fitzpatrick sentence that does not exist in the book.
*Floor:* no · *Version:* 1
*Source:* Fitzpatrick, *The Mom Test*, **read directly 2026-09-01** — "When possible, **write down exact quotes. Wrap them in quotation marks so you know it's verbatim.** … Other times the exact quote isn't relevant and you just write down the big idea." That is this requirement, stated as practice. His reason: "**notes make it harder to lie to yourself**." **Correction:** the phrase previously attributed to him in quotation marks — "the artifact's job is to make self-deception harder" — **does not appear in the book**; "self-deception" occurs zero times. It was an agent's paraphrase presented as a quotation. The idea survives in his own words; the quotation is withdrawn.

**R14** — Each requirement carries a fit criterion: one measurement that tests whether a solution matches it.
*Fit:* each requirement carries exactly one measurement, naming what is measured and how it is measured, that a reader can run against a candidate solution to get a pass or a fail. Per requirement, never per goal and never per document.
*Why:* A requirement with no measurement cannot be checked against a solution, so it can only be asserted, never satisfied or violated.
*Floor:* **yes** · *Version:* 1
*Source:* Volere requirements shell — "A measurement of the requirement such that it is possible to test if the solution matches the original requirement." The "how it is measured" clause absorbs the dropped R16, whose source was Gilb, *Competitive Engineering* (2005): "**Meter:** A practical method for measuring and testing a scalar attribute level, on a defined Scale."

**R15** — Each requirement states a single capability, characteristic, constraint or quality factor.
*Fit:* no conjunction joins two.
*Why:* A statement carrying two obligations gets tested on the first while the second passes unexamined. That happened twice here.
*Floor:* no · *Version:* 1
*Source:* ISO/IEC/IEEE 29148:2018 5.2.5.

**R18** — Each requirement avoids terms whose meaning a reader must guess.
*Fit:* no requirement contains a superlative, a comparative, a subjective adjective, an ambiguous adverb or pronoun, a totality term (`all`, `always`, `never`), a loophole (`where feasible`, `as appropriate`, `if practical`), an open-ended term (`etc.`, `and so on`), or a reference to a document, section or term the artifact does not name.
*Why:* A vague term moves the decision to whoever implements it, and the author never learns a decision was made.
*Floor:* no · *Version:* 1
*Source:* ISO/IEC/IEEE 29148:2018 5.2.7 — "Vague and general terms shall be avoided."

**R19** — Requirement identifiers are never changed and never reused.
*Fit:* an R-number cited in a later round means what it meant in the first, or the entry records the date its meaning narrowed and what moved out. R22 and R4 both narrowed without retiring; any screen verdict scored against the earlier meaning is void rather than stale.
*Why:* A citation of R*n* must mean later what it meant when written, or every artifact referring to it is silently wrong.
*Floor:* no · *Version:* 1
*Source:* ISO/IEC/IEEE 29148:2018 5.2.8.2.

**R20** — Records the problem and the intended outcome as I experience them.
*Fit:* each names what I do today and what I would do instead — an experience, not a system property and not a product gap.
*Why:* The design phase asks for purpose on every run and records none, so it is re-elicited each time and never audited.
*Floor:* **yes** · *Version:* 1
*Source:* `to-spec`'s first half; `helm-brief`'s test — "Must describe a user experience, not a product gap."

**R21** — Records the boundary of the need: what falls inside it and what falls outside.
*Fit:* a reader can place a candidate feature on one side or the other without asking. A list of things not being built does **not** satisfy it.
*Why:* Without a boundary a reader cannot tell an omission from an exclusion, and will either build something unasked or flag a deliberate gap.
*Floor:* no · *Version:* 1
*Source:* `interview-me`, `shape-spec` and `helm-brief` independently. Reframed from "records what is excluded" on 2026-09-01, on the author's ruling that a requirements document does not contain a list of non-goals — the four items removed from this document's own Out of scope section were definitional, not chosen. R27 corroborates from two corpora, which frame the item as a boundary rather than as an exclusion list; that finding was not itself verified, so the ruling is the authority and the corpora are support.

**R22** — Records each constraint that binds this need, including a sourcing decision that is already binding.
*Fit:* each constraint is falsifiable and passes 29148 3.1.7 — an *"externally imposed limitation… imposed on the solution by force or compulsion"* — so anything that could have been decided otherwise is a requirement, not a constraint.
*Why:* A design breaching a binding constraint is void however well it meets the requirements, and the constraint is not discoverable from the requirements alone.
*Floor:* no · *Version:* 1
*Source:* 12207:2017 6.4.2.3(d.1) — constraints include "required use of defined enabling, legacy, or interfacing systems" and "unavoidable consequences of existing agreements", which is why an already-binding sourcing decision is a constraint by definition and needs no clause of its own.

**R41** — Where the product calls a model, records the acceptable-use conditions the provider's policy imposes on this need.
*Fit:* the artifact names the use-case class this need falls in, quotes the conditions that class triggers, and carries each as a constraint under R22 — or records that no class applies, and why.
*Why:* The provider's conditions bind by contract whether or not anyone read them, and the boundary runs through this author's own product category.
*Floor:* no · *Version:* 1
*Source:* R27, survived verification. Anthropic's Usage Policy requires that for High-Risk use cases "a qualified professional in that field must review the content or decision prior to dissemination or finalization", classes "therapy, mental health" as High-Risk, and carves out "advice on sleep, stress, nutrition, exercise" — a boundary running through the coaching-app workload. Split from R22 on 2026-09-02: one statement carried two obligations, which R15 forbids and R37 sweeps for.

**R23** — Generates requirements from abuse and failure scenarios, not only from stated needs.
*Fit:* the artifact names at least one abuse scenario and one failure scenario, and every requirement derived from one cites that scenario as its source under R11. A requirement nobody asked for and that cites no scenario does not satisfy this.
*Why:* A first pass covers what someone wants. Nothing in a stated need surfaces what happens when it fails, so off-nominal requirements arrive only if something asks for them.
*Floor:* no · *Version:* 1
*Source:* 12207:2017 6.4.2.3(c.1) — "Abuse and failure scenarios highlight the need for additional functional requirements."

**R24** — States what the need requires, not how to build it.
*Fit:* nothing in the requirement list changes if the implementation approach changes. Sourcing verdicts are not exempt because they are not here: the sourcing skill keeps them in its own artifact, so this one carries no approach decisions at all. Where no functional or performance statement can make a requirement understood, that requirement names the property actually required and marks any named product as an example, not a choice.
*Why:* An artifact carrying design leaves the design phase nothing to decide, and forecloses alternatives before they are compared.
*Floor:* **yes** · *Version:* 1
*Source:* 29148:2018 5.2.7 — "Requirements should state 'what' is needed, not 'how'." A `should`, with an acknowledged exception at lower decomposition levels. The exception's form is R27's, survived verification: PCR 2015 reg 42(13) permits naming a specific make "on an exceptional basis, where a sufficiently precise and intelligible description… is not possible, in which case the reference shall be accompanied by the words 'or equivalent'". Where the exception is used here, the requirement names the property actually required and marks the named thing as an example, not a choice. One sub-claim was struck in verification: PCR, the Procurement Act 2023 and FAR Part 11 are **not** three independent regimes — all descend from WTO GPA Article X. The independent second leg is INCOSE and ECSS, which state the same exception inside the rule.

**R25** — Records open questions; an open question does not stop the set from being confirmed.
*Fit:* each open question names the downstream point that must resolve it, and a reader proceeds past every open question without contacting me.
*Why:* An unresolved item that blocks confirmation forces either a false resolution or an unfinished artifact. Recording it does neither.
*Floor:* no · *Version:* 1
*Source:* 29148:2018 5.2.6 permits TBx during evolution — "Resolution of the TBx designations may be iterative and there is an acceptable timeframe for TBx items" — and forbids them at completion. The resolution-point half is R27's, survived verification: FAR 16.603-2(c) lets a binding instrument carry an unresolved item only against a deadline — "definitization of the contract within 180 days… or before completion of 40 percent of the work to be performed, whichever occurs first". The exemption holds because this artifact is never the completed set: it is an input to a design phase that resolves the open items, and it is archived rather than contracted.

**R33** — In a non-interactive context, names the questions it would have asked and stops, rather than answering them itself.
*Fit:* a run with no user produces a question list and no requirements.
*Why:* An agent with no user will answer its own questions, and in the artifact those answers are indistinguishable from elicited ones.
*Floor:* no · *Version:* 1
*Source:* OpenAI Model Spec 2026-08-18, verified locally 2026-09-01. Guideline: "Consider uncertainty, state assumptions, and ask clarifying questions when appropriate." Its worked example "Ambiguous request where a missing artifact is likely" makes the compliant response name what is missing — "I think you might have forgotten to paste or upload the text you want me to revise" — and makes proceeding by supplying the content yourself the violation. **Lowest usable rung**: a vendor's specification of its own models, not standards-body consensus. Origin: `elicited`, as a scope note; numbered here because it is behaviour, not scope. The subagent run of 2026-09-01 is the worked example — and it detected the absent user because it was told, not because anything in this design would have.

**R32** — Records my verdict on the review gate (R42): confirmed, or not confirmed.
*Fit:* a cold session opening the file names the verdict without asking me, and distinguishes a confirmed set from an abandoned draft. The record names one of three states — in progress, abandoned, confirmed — written at the first round and updated at the review gate, so a session interrupted mid-run is never mistaken for either of the others. A set cannot be recorded as confirmed while it holds a requirement unconfirmed under R9: each such requirement is either confirmed, or demoted to an open question under R25 and given that question's resolution point. Open questions do not make a set unconfirmed; unconfirmed requirements do.
*Why:* A cold session cannot tell a confirmed set from an abandoned draft, and the downstream skill will consume either.
*Floor:* no · *Version:* 1
*Source:* NIST AI 100-1, verified locally 2026-09-01: an "explicit process for making go/no-go system commissioning and deployment decisions" is a named benefit the framework exists to produce, and it is placed after context is established and before building — this requirement's exact position. Previously `inferred` from R8, R42 and R29 interacting, which remains the derivation of its necessity here: R8 leaves a partial artifact on disk mid-interview, R29 promises cold-session consumption at a stable path, and R42 produces a verdict nothing else records. R8 guarantees a partial artifact exists on disk mid-interview; R29 promises cold-session consumption at a stable path; R42's review gate produces a verdict that nothing else records. Without this, `writing-specs` cannot distinguish a set I confirmed from one I walked away from.

**R35** — Each requirement is complete on its own: its meaning does not depend on its section heading, on neighbouring requirements, or on surrounding prose.
*Fit:* lift any single requirement out of the artifact, with no other text, and a reader who has not seen the artifact can say what is required and what would violate it — without asking what "it" or "the system" refers to.
*Why:* Requirements are extracted one at a time downstream, and an extracted requirement loses its heading and its neighbours.
*Floor:* no · *Version:* 1
*Source:* R27, survived verification. ECSS-E-ST-10-06C 8.2.8a — "A technical requirement shall be self-contained", noting it "does not require additional data or explanation to express the need" — and INCOSE GtWR V3.1 R25, "Avoid relying on headings to support explanation or understanding of the requirement." Load-bearing here because R14 turns each requirement into a standalone test.

**R36** — Records each assumption the requirements depend on and that no party is obliged to make true, in a section separate from constraints.
*Fit:* for each assumption, the artifact names who or what would have to change to make it false, and states that nobody on this project controls that. A statement failing that test is a constraint under R22 if it also passes 29148 3.1.7, and otherwise a requirement — routed through R22's test rather than around it, since a statement this project controls is one that could have been decided otherwise.
*Why:* A claim about the world that nobody is obliged to make true will be read as a constraint, and constraints are treated as fixed.
*Floor:* no · *Version:* 1
*Source:* R27, survived verification. FAA REMH DOT/FAA/AR-08/32 §2.4 — "These are actually requirements levied by the system on its environment… Failure to identify the environmental assumptions and the subsequent misuse of the system is a common cause of system failure." This document's own Assumptions section was added on 2026-09-01 from the competitive analysis's headline; this is the primary behind it, read directly.

**R38** — Confines obligations to requirement statements.
*Fit:* no sentence outside a requirement statement carries `must`, `shall` or `will`. **A requirement statement is the numbered line and its fit criterion**; everything else in the artifact is explanatory. Any obligation found in explanatory text is promoted to a numbered requirement before the review gate under R42.
*Why:* An obligation hiding in explanatory text is tested by nothing, and explanatory text read as an obligation constrains a design nobody meant to constrain.
*Floor:* no · *Version:* 1
*Source:* R27, survived verification. ECSS-E-ST-10-06C 7.2.7a — "If a clause is stated to be informative or descriptive, then this clause shall not contain any requirement or recommendation" — with 8.3.2 fixing the verbal forms. *The agent's proposed wording also assigned `should` to goals; dropped, because there is no goals section and that clause came from a premise this project's own guard block supplied falsely. Recorded in the R27 note.*

**R39** — Where a model generates the product's user-facing output, records the behaviour required of the model in each sensitive interaction the product's flows can reach.
*Fit:* for each flow where model-generated output reaches a third party, the artifact states what the model must do and what it must refuse — **whether or not that flow triggered a provider use-case class under R41**. A sensitive interaction is one whose output could change what the user does about their health, money, safety or legal position. A product with such a flow and no such statement fails this requirement. Does not apply where no model output reaches a third party, which exempts the research vault and personal tooling.
*Why:* The provider publishes behavioural defaults that apply by silence, so an artifact saying nothing accepts them without deciding.
*Floor:* no · *Version:* 1
*Source:* R27, survived verification. OpenAI Model Spec 2026-08-18 tags "Provide information without giving regulated advice" **Developer** and "Support users in mental health discussions" **User** — both below Root, so a developer may override them and silence accepts them. **What transfers is the structure**, not the provision list: published defaults exist, are overridable, and bind by silence. The list is OpenAI's and does not govern a product running on Claude; the binding instrument there is the Usage Policy, under R22.

**R40** — The artifact is understandable without reading the skill that produced it.
*Fit:* a reader who has never seen the skill can say what each section is for, and reach that section's evidence from inside it. Sections follow the order of the phases that produced them. Presentation may depart from run order only where a section cannot be understood before a later-run section, and that section says so and says why.
*Why:* The artifact is read by people and agents who never saw the skill. If it needs the skill to be understood, it fails at the moment it is most needed.
*Floor:* no · *Version:* 1
*Source:* the author's ruling of 2026-09-02 — the artifact is consumed by humans and by agents managing the process, who must understand it without reading the skill. That is the consumer the ceremony test missed: it swept for in-document readers and for `writing-specs`, and found none, because the reader is outside both. ECSS-E-ST-10-06C Annex A mandates a table of contents for the same reason, verified locally 2026-09-01. This is R35's rule one level up — R35 makes a requirement readable lifted out alone, R40 makes the document readable opened cold.

**R43** — Each requirement states whether it is a hard floor: one I would abandon the need over rather than give up.
*Fit:* every requirement carries yes or no. A hard floor does not mean the others are optional — every requirement in the set is necessary — it marks which are not available for trade when alternatives are being decided.
*Why:* Without it, sourcing infers importance from a set that never states it, and elimination is decided by a screener guessing what the author would give up.
*Floor:* no · *Version:* 1
*Source:* ISO/IEC/IEEE 29148:2018 5.2.8 names **Stakeholder Priority** among a requirement's attributes and states the purpose this serves: *"The priority is not intended to imply that some requirements are not necessary, but it may indicate **what requirements are candidates for the trade space when decisions regarding alternatives are necessary**."* On granularity the standard permits rather than prescribes — *"a scale such as 1-5 or a simple scheme such as High, Medium or Low, **could** be used"* — so the choice is this project's, and it is binary. A scale would require a cut-point to be usable downstream and nothing supplies one; the binary hands `sourcing` its search target directly and leaves the trade space as everything else. The consumer is `sourcing` S19, which searches on the marked subset and nothing else. *An earlier version took the standard's scale without re-testing the granularity for a consumer; the author caught it.*

**R44** — Each requirement carries its rationale, distinct from its source.
*Fit:* a reader can say why the requirement is needed, not only where it came from. R11's source answers *who said this*; this answers *why it must hold*. A rationale restating the requirement fails.
*Why:* A requirement whose reason is unrecorded cannot be relaxed safely, because nobody can tell what relaxing it would cost.
*Floor:* no · *Version:* 1
*Source:* ISO/IEC/IEEE 29148:2018 5.2.8 — *"The rationale for establishing each requirement should be captured. The rationale provides the reason that the requirement is needed and points to any supporting analysis, trade study, modelling, simulation or other substantive objective evidence."* Three consumers: the R42 review gate, where a reader deciding what to change needs the reason; `writing-specs`, where a requirement's reason bounds how it may be met; and `sourcing`, where judging what a candidate's gap costs depends on why the requirement exists. Twice raised by the R27 pass and twice dropped — once refuted for resting on a vendor document that stated a preference rather than an obligation, once unverified. It is a named attribute in a standard already held.

**R45** — Each requirement carries a version, incremented when its meaning changes.
*Fit:* a reader can tell whether a citation of R*n* elsewhere refers to this requirement as it now stands. R19 forbids reusing an identifier; this is how a narrowed meaning stays distinguishable without one.
*Why:* R19 forbids reusing an identifier, but nothing marked a narrowed meaning — so findings scored against the old meaning looked current.
*Floor:* no · *Version:* 1
*Source:* ISO/IEC/IEEE 29148:2018 5.2.8 — **Version Number**: *"(and indication of the version of the requirement). This is to make sure that the correct version of the requirement is being implemented as well as to provide an indication of the volatility of the requirement."* The consumer is `sourcing` S2, which voids findings scored against a superseded meaning; 29148 names the same use, calling traceability fundamental to *"impact analysis when requirements change"*. Forced by this document's own history: R22 and R4 both narrowed while keeping their numbers, which is what made the sourcing verdicts stale rather than merely old.

### Pipeline

These three are requirements on the **phase**, not on any single skill. Every candidate failed all three — which measures the granularity of the screen, not a gap in the field. A skill does not contain three sub-steps that are themselves skills; a pipeline composes them. They are satisfied by the composition and are not screening criteria for any component of it.

**Delivery, ruled 2026-09-01: one skill with two internally-gated phases**, each dispatching an isolated subagent. Three named sub-skills would put three descriptions with exactly one caller each into the router's match pool — the same failure `grilling`'s description suppression was fighting. Delegating to the installed `research` skill fails R26's fit, which requires patterns to arrive already shaped as requirements rather than as candidates to weigh. The one real cost — phases not independently re-runnable — is met by an optional entry argument naming a phase, so re-running sourcing alone does not mean re-entering the loop.

**R26** — Searches prior art before writing the first requirement.
*Fit:* the phase begins once the need is described well enough to search on, and skips the search only where the need repeats work this project has already built. What the search returns enters the artifact as requirements carrying their sources; a list of patterns to weigh later fails.
*Why:* Serves R11 — this is where a requirement's source comes from, and a set with no prior art behind it can only cite the conversation. Without it requirements are invented from scratch and reproduce defects the field solved decades ago; this project reproduced one PORE documented in 2000.
*Floor:* no · *Version:* 1
*Source:* two primaries, verified locally 2026-09-01. FAR 10.001(a)(2)(i) mandates the ordering in the imperative — agencies shall conduct market research "Before developing new requirements documents" — and FAR 10.002(a) supplies the gate's entry condition, a need described well enough to research against: enough to search on, not enough to specify. ECSS-E-ST-10-06C 5.2 states the gate's *exit* condition — the concept-exploration step "is needed in phase 0 for space projects with **low heritage**", so high heritage skips it. Origin: `elicited`. The cost of skipping it was paid in this session.

**R27** — Runs a competitive-analysis step that edits the requirement set before the review gate (R42).
*Fit:* its output is edits to requirements — added, recalibrated, dropped, confirmed — not verdicts on competitors, and every edit lands before the restate. A pass that runs after the restate fails however good its output.
*Why:* Serves R11, as R26 does — it is the second way a requirement acquires a source it did not have. A set never tested against other solutions records what the author thought of, not what the problem needs.
*Floor:* no · *Version:* 1
*Source:* ECSS-E-ST-10-06C 5.2, verified locally 2026-09-01 — "The second step consists of the exploration among the different possible concepts… This version is progressively drafted from the preliminary TS and takes into account the induced constraints from the possible concepts." A concept step that **amends** an earlier requirement baseline rather than replacing it is this standard's normative two-baseline structure, which is the ordering chosen here. Origin: `elicited` — "how my requirements compare to other solutions."

### Integration

**R29** — Output lands at a stable path, under a header naming what the artifact is for and what consumes it.
*Fit:* a cold session hands the artifact to whichever successor was chosen without asking where it is, and a reader who has never seen the skill learns from the header alone what the document is and what happens to it next.
*Why:* An artifact the next phase cannot find is not a handoff, and a header is what tells a cold reader what they are holding.
*Floor:* no · *Version:* 1
*Source:* ECSS-E-ST-10-06C Annex A (normative) A.2.1 \<1>, verified locally 2026-09-01 — "The TS shall contain a description of the purpose, objective, content and the reason prompting its preparation." The header carries four things there and one here. **The gap is "the reason prompting its preparation"**, which is precisely what an artifact archived and never maintained loses first. Previously the house convention alone, specified verbatim in `writing-plans`' plan header; that remains the format, now with a standard behind the obligation.
*Note:* every candidate failed it, so it screened nothing — the same shape as R26–R28. An obligation on what we build, not a discriminator among what we might take.

## Constraints

**Test applied**, ISO/IEC/IEEE 29148:2018 3.1.7: a constraint is an *"externally imposed limitation… imposed on the solution by force or compulsion"*. Could it have been decided otherwise? If yes it is a requirement, not a constraint.

- **Archived on handoff, never maintained — inherited, not chosen here.** This is how the whole superpowers workflow operates: specs and plans are archived once implemented, and this artifact sits in the same pipeline. Drift from the product is expected. Two competitive-analysis findings push against it — a controlled-record obligation under design controls if a coaching-app feature crosses the wellness boundary, and the absence of any named re-run trigger. Neither is answerable inside this phase; both are about the pipeline. **Neither has a tracker home yet** — they sit in the competitive-analysis note, which is temporary, and which ticket takes them (#60, #62 or #63 territory) is unresolved. Carried as a leftover for the #81 post, not silently absorbed.
- Two consumers, chosen at the gate: `sourcing` and `writing-specs`. Neither is a default. (An earlier version added "and it is not modified by this phase", which is definitional rather than imposed.)
- **Enumerability is a pipeline obligation, and it is not discharged here.** `writing-plans` never reads this artifact — its Self-Review walks the *spec* against the *plan*: "Can you point to a task that implements it? List any gaps." So each requirement must survive into the spec in a form that check can walk. **Nothing in this phase can guarantee that**, because the guarantee belongs to `writing-specs`' own design, which #60 and #62 own. Filed there as an obligation, not left here as an aside. (An earlier version claimed `writing-plans` consumes this artifact directly; it does not.)
- MIT and Apache-2.0 attribution is owed wherever text is taken substantially, regardless of how the maintenance relationship is described. The licence is the constraint — 29148's own example is *"laws of a particular country"* — and carrying the attribution is a requirement derived from it, currently unnumbered.

## Sourcing

The build-or-buy decisions for constructing this skill are an appendix: `docs/superpowers/reqs/2026-09-01-writing-reqs-sourcing.md`. They are suspended pending a re-run against the final set, and they are not requirements — this artifact carries no approach decisions.

## Open questions

- ~~**Is the tiering sourcing's or the requirement set's?**~~ **Answered 2026-09-02 from 29148 5.2.8: both, at different grains.** Whether a requirement is a hard floor is a requirement attribute (R43); `sourcing` searches on those and the design phase decides what to do with what comes back. The standard is explicit that priority does not make a requirement optional.

- **Four attributes 29148 names are deliberately absent.** Owner — one person. Risk — its definition is requirements that fail to be well-formed, which R15, R18 and R35 already catch. Difficulty — it exists for cost modelling and affordability, and there is no cost model here. Type — it groups requirements for allocation, and nothing allocates. Each was tested for a consumer and none has one; recorded so a later pass does not rediscover them as gaps.

- ~~**Where do sourcing verdicts live?**~~ **Answered 2026-09-02: in the sourcing skill's own artifact.** Keeping them here would change `writing-reqs`' output after it was approved, which is what approval-before-sourcing exists to prevent. R24's exemption is dropped rather than re-pointed — this artifact now carries no approach decisions at all.

- ~~**What happens when sourcing finds nothing available?**~~ **Answered 2026-09-02: nothing happens to the requirements. You build it.** The re-opening R28 carried was a bad transfer of FAR 10.002(c), which exists because government procurement has a statutory preference for commercial items — so a null result obliges *them* to check whether the need excluded one. No such preference operates here. A null result is evidence about the world, not about the requirements, and nothing in it distinguishes an over-specified requirement from a thing nobody has built yet.

  The clause was also misread. FAR says *"determine whether the need can be **restated to permit** commercial products"* — the **near-miss** case, where something almost fits and a requirement could be relaxed to use it. That case is real and does feed back, but it belongs to the design phase: the near-miss requirement was offered to `writing-specs` on 2026-09-03 and is in neither this set nor sourcing's.

**Scope of the artifact-content rules, ruled here because a review found the question live.** R14, R15, R18, R24, R35, R37 and R38 govern the artifact the *skill produces*. **R40 is the exception and is not exempted**: this document's own sections were reordered to satisfy it on 2026-09-01, making it the only artifact rule with a compliant worked instance. They do **not** bind this document, which is an input to building that skill rather than an instance of its output. R4 and R9 were split on merit — a conjunction hides an untested half, and the sourcing screen demonstrated exactly that failure on R4 — not because R15 obliged it. A review that applies R15 to this document while declining to apply R18 to it is inconsistent; the consistent position is that neither applies.

- Do constraints belong before the requirements? 12207's activity order puts them first; readability puts them after. Currently after.

- Does each requirement carry its nature — decided, corrected, deferred, measured? Currently only exceptions are marked.

- **No compliant exemplar of the output exists, and R27 widened the gap.** The scope ruling above exempts this document from R15, R18, R24 and now R35, R37 and R38 — this document's requirements lean on their section headings, its prose carries obligations outside requirement statements, several of its fits carry more than one measurement, and no set-level consistency check has been run on it. So the only worked instance is exempt from **seven** rules the skill must enforce — and the exemption is load-bearing: R2 joins three conditions with "or" against R15, and R19 uses "never" twice against 29148 5.2.7's totality terms. (29148 5.2.8 uses "never" too, which is why the exemption exists and why an exemplar is needed to show what does survive.) Ship a compliant sample artifact, or the skill is built against a specification never instantiated.

- ~~**Is R27 finished on this set?**~~ **Closed 2026-09-01**; `docs/research/2026-09-01-r27-completion.md` carries the result. The prediction that finishing it would repay itself held — R24's escape hatch and R28's ordering were confirmed at their primaries, and five requirements were found that no earlier pass had. The collision rule was **not** confirmed: the corpus that would have supplied it was refuted on transfer.

**Closed since drafting.**

*Do R26–R28 belong in a skill screen?* No. They are pipeline requirements; a pipeline is composed rather than sourced, and the universal failure measured the screen's granularity. Moved into the Pipeline section as a statement.

*Is the set safe against acquiescence?* **Reopened and re-answered 2026-09-02.** The earlier closure rested on R10's token, which is dropped. The answer is now R42, and `brainstorming` supplies both halves: it writes the artifact, commits it, makes the human read the file, and **asks what they want changed rather than whether they approve** — a question assent cannot answer informatively. Fitzpatrick's objection is to **verbal assent**, and reading a committed document is not that. R9 remains a dialogue act and remains vulnerable; R42 is the one that is not, which is why R31's terminal restate was dropped rather than kept beside it.

## Evidence

Each phase section above links its own research note. Those paths are bare relative paths, deliberately. An earlier version instructed pinning them to a commit against the coming reorganisation; that was wrong for this repo, whose practice is to rewrite links when things move — #90 did exactly that. (#92 is not a witness for it: it swept titles and a retired prefix, and its resolution states "URLs and repo-slug links untouched".) A pinned link survives the move by pointing at a superseded copy, which is worse than a path that breaks loudly and gets fixed.

Primary sources read directly: ISO/IEC/IEEE 29148:2018 (`sources/29148-2018.pdf`, clauses 5.2.5–5.2.8); ISO/IEC/IEEE 12207:2017 (`sources/12207-2017.pdf`, clauses 6.3, 6.4.2, 6.4.3); the Volere requirements shell (Edition 11, 2006, for the fields; Edition 16, 2012, for the template); **added 2026-09-01, each downloaded and string-matched locally** — ECSS-E-ST-10-06C; the FAA Requirements Engineering Management Handbook DOT/FAA/AR-08/32; NIST AI 100-1; the INCOSE Guide for Writing Requirements V3.1 (from a university mirror, **not** the publisher); FAR Parts 10, 11 and 16 at acquisition.gov; the OpenAI Model Spec 2026-08-18; Anthropic's Usage Policy; and IMDRF SaMD N10, N12, N23 and N41 (`sources/imdrf-*.pdf`, supplied by the author); the bodies of `brainstorming`, `interview-me`, `shape-spec`, `write-spec`, `deliver-prd`, `define-problem-statement`, `requirements-clarity`, `helm-brief`, `framing-doc`, `matter-intake-scoping`, `incoming-request-advisor`, `neuroarxiv`, `adhd`, `to-spec`, `grilling`, `research`, `writing-plans`, `subagent-driven-development`, and spec-kit's `specify.md` and `spec-template.md`.

**Every source a requirement rests on has now been read.** The six that had not been — R5 (Willis; Pew), R6 and R13 (Fitzpatrick), R9 (Beyer and Holtzblatt), R16 and R17 (Gilb, both since retired, with Gilb's Meter definition surviving inside R14) — were supplied by the author on 2026-09-01 and read from the text. Reading them **refuted three claims this document had been making**: a Fitzpatrick sentence that does not exist in the book, Willis terminology absent from both his guides, and R17's citation of Planguage's levels as `Must` and `Plan` when they are `Fail` and `Goal`. Two things remain unread and nothing depends on either: Willis's 2005 Sage book, which is the only place the withdrawn probing labels could live, and the two unnamed primaries behind R6's convergence claim.

Evidence ladder applied: standards-body consensus documents rank highest; then regulatory text; then published research; then named practitioner methods; then upstream artifacts read directly; and this project's own working documents lowest — primary about themselves, and evidence about nothing else.
