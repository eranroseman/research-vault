# Prior art: what a requirement must carry, and what a requirements document needs

Research note, 2026-09-01. Feeds the requirements for `writing-reqs`, the pre-spec phase — see `docs/superpowers/reqs/2026-09-01-writing-reqs.md`.

**Question asked:** how is this class of problem — turning a need into a written, verified statement of what and why — solved well elsewhere? Patterns, not vendors. A pattern costs nothing to take, so nothing here needs a disposition.

**Why it was run.** Six agent-skill designs had converged on roughly six fields (goal, problem, success, scope, out-of-scope, open questions), but all six were written in the same two-year window by people in the same ecosystem, so the convergence could be imitation rather than discovery. This tested it against traditions that predate them.

**Result, stated up front:** the convergence is **rediscovery, and lossy**. The Volere requirements shell had the per-requirement shape in the mid-1990s, including two fields all six modern designs dropped.

______________________________________________________________________

## Volere requirements shell — the strongest single finding

Suzanne and James Robertson, Atlantic Systems Guild. Shell fields read from Edition 11 (February 2006); document template contents from Edition 16 (2012).

The shell is a **per-requirement card**. Its fields, with the glosses printed on the card:

| Field                    | Gloss                                                                                                              |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| Requirement #            | Unique id                                                                                                          |
| Event/use case #'s       | List of events / use cases that need this requirement                                                              |
| Requirement Type         | The type from the template                                                                                         |
| **Description**          | A one sentence statement of the intention of the requirement                                                       |
| **Rationale**            | A justification of the requirement                                                                                 |
| **Originator**           | The person who raised this requirement                                                                             |
| **Fit Criterion**        | A measurement of the requirement such that it is possible to test if the solution matches the original requirement |
| Customer Satisfaction    | Degree of stakeholder happiness if implemented. 1 = uninterested to 5 = extremely pleased                          |
| Customer Dissatisfaction | Measure of unhappiness if not part of the final product. 1 = hardly matters to 5 = extremely displeased            |
| Priority                 | A rating of the customer value                                                                                     |
| Conflicts                | Other requirements that cannot be implemented if this one is                                                       |
| Supporting Materials     | Pointer to documents that illustrate and explain this requirement                                                  |
| History                  | Creation, changes                                                                                                  |

**Why it fits.** Description + Rationale + Originator + Fit Criterion is requirement, why, source and check — on one card. `Fit Criterion` is the field every modern candidate drops, and it is the one a downstream planning phase needs in order to write a test. `Originator` is the provenance tag six separate agent skills were each solving independently.

**And the document has a section for sourcing.** Volere's 27-section template, in five groups, includes *Project Drivers* (Purpose, Stakeholders), *Project Constraints* (Mandated Constraints, Naming Conventions, **Relevant Facts and Assumptions**), *Functional Requirements* (Scope of the Work, Scope of the Product, Functional Requirements), eight classes of non-functional requirement, and *Project Issues* — including **18. Open Issues** and **19. Off-the-Shelf Solutions**.

So build-or-buy is a numbered section of a requirements specification, kept separate from the requirements themselves.

**Caveat.** The shell's `Priority`, `Customer Satisfaction` and `Customer Dissatisfaction` fields are planning apparatus for an organisation choosing what to build first. They do not transfer to a one-person setting and are not taken.

______________________________________________________________________

## ISO/IEC/IEEE 29148:2018 — read from the primary

Read directly from `sources/29148-2018.pdf`, clauses 5.2.5 through 5.2.8. Earlier passes reached this only through a reproduction in a third-party paper, which was accurate on the names of the characteristics and lossy on their content; four things the reproduction dropped are recorded below.

### Characteristics of an individual requirement (5.2.5)

"Each stakeholder, system and system element requirement **shall** possess the following characteristics."

Necessary · Appropriate · Unambiguous · Complete · Singular · Feasible · Verifiable · Correct · Conforming.

**Necessary**, verbatim: *"The requirement defines an essential capability, characteristic, constraint and/or quality factor. If it is not included in the set of requirements, a deficiency in capability or characteristic will exist, which cannot be fulfilled by implementing other requirements."*

This is the test that makes "a requirement is a must" a checkable claim rather than an assertion.

### The note the reproductions drop

Under **Appropriate**, NOTE 1:

> *"including design solutions in the requirements creates the risk that potential design solutions could be overlooked or eliminated. Examples include stating requirements that express an exact commercial system set or **a system that can be bought rather than made**"*

The standard names *"we will use library X"* as an inappropriate **requirement** — and its remedy in the same note is to put it in an attribute (5.2.8, e.g. rationale) instead. Combined with Volere's section 19, both traditions agree: sourcing belongs in the document, not in a requirement.

### Characteristics of a set (5.2.6)

Complete · Consistent · Feasible · Comprehensible · Able to be validated.

**Complete** forbids TBx — *"the set does not contain any To Be Defined (TBD), To Be Specified (TBS), or To Be Resolved (TBR) clauses"* — but is softer than usually reported: *"Resolution of the TBx designations may be iterative and there is an acceptable timeframe for TBx items, determined by risks and dependencies"*, and NOTE 2 says TBx during evolution is *"common"*.

### Requirement language criteria (5.2.7)

This clause is the requirements-smells catalogue, in the standard, predating the 2017 research paper usually cited for it. *"Vague and general terms shall be avoided."* The named classes: superlatives; subjective language; vague pronouns; ambiguous adverbs and adjectives, and **ambiguous logical statements ('or', 'and/or')**; open-ended non-verifiable terms; comparative phrases; loopholes; **terms that imply totality ('all', 'always', 'never', 'every')**; incomplete references.

Two of those — totality terms and incomplete references — appear in no secondary summary consulted.

The clause also carries the no-how rule and the assumption rule:

> *"Requirements **should** state 'what' is needed, not 'how'."* — a `should`, immediately qualified: *"However, as requirements are allocated and decomposed through the levels of the system, there can be recognition of design decisions/solution architectures defined at a higher level."*

> *"**All assumptions made regarding a requirement shall be documented and validated** in one of the requirement's attributes in 5.2.8 (e.g., rationale) associated with a requirement or in an accompanying document."*

The assumption rule is a `shall`, and it is per requirement.

### Attributes (5.2.8)

**Identification:** *"Once assigned, the identification is unique — it is never changed (even if the identified requirement changes) nor is it reused (even if the identified requirement is deleted)."*

______________________________________________________________________

## ISO/IEC/IEEE 12207:2017 — read from the primary

Read directly from `sources/12207-2017.pdf`, clause 6.4.2, Stakeholder Needs and Requirements Definition.

### Outcomes as a completeness test (6.4.2.2)

Nine outcomes, of which four bear directly:

- (e) *"Stakeholder needs are **prioritized and transformed** into clearly defined stakeholder requirements."*
- (f) *"Critical performance measures are defined."*
- (g) *"**Stakeholder agreement** that their needs and expectations are reflected adequately in the requirements is achieved."*
- (i) *"Traceability of stakeholder requirements to stakeholders and their needs is established."*

**Outcome (e) locates prioritisation.** The down-select runs on *needs*, upstream of the requirement. What survives becomes a requirement, so requirements are all musts by construction, and MoSCoW-style ranking belongs one step earlier.

**Outcome (g) makes agreement a process outcome** — which puts this tradition against the customer-discovery position that verbal assent is the wrong termination signal. Both are recorded; the disagreement is real.

### Constraints have four named sources (6.4.2.3 d.1)

> *"These constraints can result from 1) instances or areas of stakeholder-defined solution; 2) implementation decisions made at higher levels of system hierarchical structure; **3) required use of defined enabling, legacy, or interfacing systems**, system elements, resources, and staff; or 4) stakeholder-defined affordability objectives. Include those that are **unavoidable consequences of existing agreements, management decisions and technical decisions**."*

This reconciles with 29148's warning above: a sourcing decision that is **already binding** is a legitimate constraint; a sourcing decision being made now is a design choice and does not belong in a requirement.

### Abuse and failure scenarios (6.4.2.3 c.1)

> *"**Abuse and failure scenarios** highlight the need for additional functional requirements (or more specific derived requirements) to mitigate risks that are identified in the abuse or failure scenarios."*

A requirement-generation technique: you produce requirements by asking how the thing gets misused, not only by asking what is wanted.

### Elicitation sources (6.4.2.3 b.2)

> *"Identification of stakeholder needs includes elicitation of needs directly from the stakeholders, **identification of implicit stakeholder needs based on domain knowledge and context understanding**, and documented gaps from previous activities."*

Agent-supplied content is a **legitimate input**, not only a hazard. It should be marked, not forbidden.

### Context of use (6.4.2.3 c.2)

Factors to identify: *"Anticipated physical, mental, and learned capabilities of the users… Workplace, environment and facilities… **Normal, unusual, and emergency conditions**… Operator and user recruitment, training and culture."*

And the critical quality characteristics named at d.2 include **health** explicitly: *"assurance, safety, security, environment, or health."*

______________________________________________________________________

## Syntax traditions

**EARS** (Mavin et al., Rolls-Royce). A sentence grammar: *"While \<optional pre-condition>, when \<optional trigger>, the \<system name> shall \<system response>."* Fits the singularity and unambiguity requirements. **Silent on** document structure, on rationale, on source, and on quantification — it says when a sentence is well-formed, never when a specification is done.

**Planguage** (Tom Gilb). Quantifies a quality requirement with `Scale` and `Meter`, and separates the failure threshold from the target: **`Must`** is the level below which the requirement fails, **`Plan`** the level aimed at. A quality with no scale of measure is not a requirement. This is the two-level threshold, thirty years before the "guardrail metric" appeared in agent PRD templates.

*Caveat, marked unverified:* Planguage was read through a mirror site rather than Gilb's own publication.

______________________________________________________________________

## The agile lineage dissents from the artifact

Recorded because it argues against the phase existing, and the argument should travel.

Jeffries: *"The card is a token representing the requirement"* — the requirement deliberately does not live in a document, and validation is a demonstration at the **end** of implementation rather than a confirmation before it. Card, Conversation, Confirmation, where confirmation is the acceptance test.

**Why it does not bind here.** The argument is correct about a world where the document substituted for conversation with a distant customer and cost weeks to write. Here the customer is in the room, the document exists because an agent cannot have the conversation, and it costs a session. The conditions that made the argument right do not hold.

Mattpocock documents the related failure for his own template: *"The template leans hard on user stories, which is the wrong shape for architectural work: you end up writing stories nobody asked for around decisions that are really about interfaces and invariants."*

______________________________________________________________________

## Requirements defects

Femmer, Méndez Fernández, Wagner and Eder, "Rapid Quality Assurance with Requirements Smells". The smell catalogue maps onto 29148 5.2.7 and adds detection tooling. **Recorded as secondary to the standard**: 5.2.7 is the older and more authoritative statement of the same list, and it carries two categories the smells literature does not.

______________________________________________________________________

## Interview technique

**The guess-attached question is a real technique, and the agent-skill rendering of it is a mutation.** Beyer and Holtzblatt's contextual-inquiry **Interpretation** principle has the interviewer state their reading back — but the guess is **backward-looking**: it reflects meaning already expressed, and is delivered as a **statement**, not attached to an unanswered question.

Where a hypothesis must precede an answer, Willis names **single-possibility probing** as the biasing form and **multi-possibility probing** as the remedy: offer the plausible alternatives, not one. Pew documents acquiescence bias, worse with an interviewer present — and an agent asking questions is an interviewer present — plus order effects.

**Restating for confirmation is standard and has two names**: contextual inquiry's *Interpretation*, and qualitative research's *member checking*. In both traditions it is **continuous and in the moment**, not concentrated into one terminal restatement.

**Anchor questions in specific past events**, not opinions, generalities or predictions. Three independent primaries converge; the strongest single agreement in the discovery corpus.

**Nobody caps question count.** Every practice caps something adjacent instead — learning goals per person-type, session length, question density. One quantified rule exists, from motivational interviewing: reflections must outnumber questions, and stacked questions are forbidden.

______________________________________________________________________

## Sources added 2026-09-01, to anchor requirements that had none

Ten requirements carried `elicited`, `assumed`, `inferred` or a house convention as their whole derivation. This section is the evidence found for them. **Every quote below was verified by downloading the primary and string-matching it locally** — not taken from an agent's report. Two apparent mismatches in the NIST text were the PDF's own line-break hyphens (`deci- sions`, `docu- mented`), not misquotation.

### FAR Part 10 — market research (acquisition.gov, FAC 2026-01)

> **10.002(a):** *"Acquisitions begin with a description of the Government's needs stated in terms sufficient to allow conduct of market research."*

> **10.001(a)(2)(i):** Agencies shall *"Conduct market research appropriate to the circumstances— (i) Before developing new requirements documents for an acquisition by that agency"*.

> **10.002(b)(1):** *"The extent of market research will vary, depending on such factors as urgency, estimated dollar value, complexity, and past experience."*

Three requirements anchor here. **R1** — a need arrives as a rough description, and that rough description is the legitimate entry state, not a defect. **R26** — the prior-art step runs *before* the requirements document, in the imperative, and 10.002(a) supplies the gate's entry condition: enough to search on, not enough to specify. **R3** — the class is not recorded as a bare fact; it is the input that scales how much process runs.

### FAA Requirements Engineering Management Handbook, DOT/FAA/AR-08/32 (June 2009)

> **2.11.7:** *"Rationale should be collected along with the development of the requirement or assumption it is explaining. This ensures that the justification is captured by the author while he or she is thinking about it… it is much simpler to record the rationale when the latency was being computed than to try to re-engineer the reasoning later."*

**R8** — writing each requirement as its answer settles rather than in one pass at the end. The reason given is about the author's attention, not about process convenience, which is the same reason the requirement exists here.

### ECSS-E-ST-10-06C (6 March 2009)

> **5.2:** *"The process to establish the technical requirements specification during Phase 0 of a project starts with the identification and evaluation of the different possible concepts… This step is needed in phase 0 for space projects with **low heritage**."*

> **5.2:** *"The second step consists of the exploration among the different possible concepts… This version is progressively drafted from the preliminary TS and takes into account the induced constraints from the possible concepts."*

> **Annex A (normative), A.2.1 \<1>:** *"The TS shall contain a description of the purpose, objective, content and the reason prompting its preparation."*

Three requirements. **R26's gate** has a stated condition — low heritage, run it; high heritage, skip — which is a gate condition rather than an assertion that a gate exists. **R27** — a concept-exploration step that *amends* an earlier requirement baseline rather than replacing it is the normative two-baseline structure here, so the ordering chosen is not unusual. **R29** — the header carries four things, and the one this project lacks is *the reason prompting its preparation*, which is exactly what an archived-and-never-maintained artifact loses first. **R40** — Annex A is a normative mandated table of contents, which is the same claim as "sections follow the phases", made by a standards body.

### INCOSE Guide for Writing Requirements V3.1 (115 pp., verified locally)

> **R29 /Uniqueness/Classify:** *"Classify needs and requirements according to the aspects of the problem or system it addresses."* Elaboration: classification helps *"identify potential duplications and conflicts"* and *"assist in identifying what needs or requirements may be missing"*.

**R3**, second leg. INCOSE classifies per requirement and treats classification as a **search device for completeness**, where R3 uses one class for the whole need as a routing label. The stronger form is available and R3 does not yet take it.

### ISO/IEC/IEEE 12207:2017 already had the risk-tier principle — three clauses, all missed

Checked 2026-09-01 after the author asked whether 12207 covers the ground IEC 62304 Ed. 2 does. It covers the principle; it does not carry a taxonomy.

> **6.4.2.3(d.2):** *"Identify the stakeholder requirements and functions that relate to critical quality characteristics, such as assurance, safety, security, environment, or health."*

> **6.4.3:** *"Identify requirements that relate to risks, criticality of the software system, or critical quality characteristics."*

> **6.3:** *"The Technical Management processes are applied with a level of rigor and formality that depends on the risk and complexity of the project."*

The first is task **2** under activity d), *"Transform stakeholder needs into stakeholder requirements"* — the task **immediately after** task 1, the constraint-sources task already cited for R22. R3's anchor sat one line below R22's and went unread through two passes.

**What is genuinely absent:** any named classification scheme. Searching the full text returns **zero** hits for "safety class" and **zero** for "62304". 12207 delegates the taxonomy rather than supplying one — NOTE 1 on 6.4.2.3(d.2) points to ISO/IEC/IEEE 15026, and bibliography reference [22] is *ISO/IEC 15026-3:2011, System and software engineering — Systems and software assurance — Part 3: System integrity levels*.

So IEC 62304's classes A/B/C are one health-specific instantiation of a tier scheme; 12207's own pointer for the general case is 15026-3. Neither is reachable from here.

### IMDRF SaMD, four documents — the taxonomy 12207 delegates

Supplied by the author 2026-09-01 after I reported them unreachable, and read from the PDFs.

**N10FINAL:2013 sets the gate by intent, not by function.** SaMD is *"software intended to be used for one or more medical purposes that perform these purposes without being part of a hardware medical device"*, and *"Mobile apps that meet the definition above are considered SaMD."* Medical purpose is the GHTF list — *"diagnosis, prevention, monitoring, treatment or alleviation of disease"* and the rest. So the boundary is what the software is **intended and claimed** to do, which is the same shape as the wellness/device line the first competitive-analysis pass found and only partly applied.

**N12FINAL:2014 is the taxonomy.** §7.2 is a 3×3 matrix:

| State of the healthcare situation | Treat or diagnose | Drive clinical management | Inform clinical management |
| --------------------------------- | ----------------- | ------------------------- | -------------------------- |
| Critical                          | IV                | III                       | II                         |
| Serious                           | III               | II                        | I                          |
| Non-serious                       | II                | I                         | I                          |

> *"The categories are in relative significance to each other. Category IV has the highest level of impact, Category I the lowest."*

**The load-bearing sentence for R3 is §7.1**, and it is about derivation rather than about the labels:

> *"The categorization relies on an accurate and complete SaMD definition statement."*

§6.0 fixes that statement's form: significance of information (treat or diagnose / drive / inform), state of the situation (critical / serious / non-serious), and the core functionality essential to the first two. **The class falls out of the statement.** R3 previously asked for a class and a reason; it now asks for the statement, because a class without one cannot be checked.

**N41FINAL:2017 supplies the scaling claim**, which is what R3 originally asserted without a source:

> *"global regulators expect that performance metrics for a SaMD have a scientific level of rigor that is commensurate with the risk and impact of the SaMD to demonstrate assurance of safety, effectiveness, and performance."*

> *"The level of evaluation and independent review should be commensurate with the risk posed by the specific SaMD."*

**N23FINAL:2015** applies QMS principles informed by the N12 category, and adds nothing R3 needs.

**Two honest limits.** IMDRF contains **zero** occurrences of "wellness", "fitness" or "lifestyle" — it does not carve out wellness, it simply does not reach software with no intended medical purpose. The carve-out document is FDA's General Wellness guidance, which is **not** in hand. And nothing in these four supports the claim, made in an earlier draft, that the tier declaration is *"a deliverable that never scales down"*; what they support is that **rigour** scales with the category. That phrasing is withdrawn.

### NIST AI RMF 1.0, NIST AI 100-1

> *"Framework users are expected to benefit from: … explicit processes for making **go/no-go** system commissioning and deployment decisions"*.

> *"After completing the MAP function, Framework users should have sufficient contextual knowledge about AI system impacts to inform an initial go/no-go decision about whether to design, develop, or deploy an AI system."*

> **MAP 1.1:** *"Intended purposes, potentially beneficial uses, context-specific laws, norms and expectations, and prospective settings in which the AI system will be deployed are understood and documented."*

**R32** — recording whether the gate passed is a named process outcome, positioned after context and class are established and before building. **R3**, third leg — documenting intended purpose and setting is placed *before* the go/no-go, which is where R3 sits.

### OpenAI Model Spec, 2026-08-18

> Guideline: *"Consider uncertainty, state assumptions, and ask clarifying questions when appropriate."*

> Worked example, *"Ambiguous request where a missing artifact is likely"*. **Compliant:** *"I think you might have forgotten to paste or upload the text you want me to revise (or the upload may have failed). Could you share it?"* — annotated *"Asks the smallest disambiguating question and stays helpful"*. **Violation:** the assistant proceeds by interpreting the request itself as the missing content.

**R33** — when the required input is absent, name what is missing and stop, rather than supplying it yourself. This is the closest published anchor found; it is a vendor's specification of its own models rather than a standards-body consensus, and it sits accordingly low on the ladder.

### R7 has no prior art and does not need any

**R7** places no cap on question count. Its evidence is a **null result** from the competitive-analysis pass: no practice surveyed caps the number of questions, and every one caps something adjacent instead — learning goals per person-type, session length, question density. A null result across a surveyed corpus is evidence, and it is competitive-analysis evidence rather than prior art. Searching both standards for any cap on elicitation effort returned nothing, which is consistent.

______________________________________________________________________

## Six sources read directly 2026-09-01, after the author supplied them

Every requirement resting on a reported-but-unread source now rests on the text. Two claims did not survive.

### Fitzpatrick, *The Mom Test* — R6 and R13

R6, verbatim, rule 2 of three:

> *"Talk about their life instead of your idea. **Ask about specifics in the past instead of generics or opinions about the future.** Talk less and listen more."*

R13, verbatim:

> *"When possible, write down exact quotes. **Wrap them in quotation marks so you know it's verbatim.** … Other times the exact quote isn't relevant and you just write down the big idea."*

with his reason: *"notes make it harder to lie to yourself."*

**One claim refuted.** The competitive analysis attributed to him, in quotation marks, *"the artifact's job is to make self-deception harder."* The string "self-deception" occurs **zero** times in the book. It was an agent's paraphrase wearing quotation marks. The idea is his; the sentence is not.

### Willis, two guides (1999 and 2012) — R5

> *"the use of probes may lead the respondent to particular types of responses… can be minimized through the careful selection of non-leading probing techniques… **rather than suggesting to the subject one possibility** ('Did you think the question was asking just about physicians?'), **it is preferable to list all reasonable possibilities**… probes should be characterized by unbiased phrasing."*

**Pew Research Center, *Writing Survey Questions*, converges on the same remedy** — read directly 2026-09-01 at `pewresearch.org/writing-survey-questions/`:

> *"This is sometimes called an 'acquiescence bias'… This behavior is even more pronounced when there's an interviewer present, rather than when the survey is self-administered. **A better practice is to offer respondents a choice between alternative statements.**"*

The same page confirms order effects and that randomisation spreads rather than eliminates them. Pew supplies both halves of R5 — the measured harm and the remedy — so R5's two legs are genuinely independent. It had previously been cited as bare "Pew", with no document, author, date or URL; that was an organisation name, not a citation.

The author supplied a second Willis document on 2026-09-01: *Cognitive Interviewing: A "How To" Guide* (1999, Research Triangle Institute, from an ASA short course). **It carries the passage above word for word** — the same physicians example, the same conclusion. A formulation stable across thirteen years and two publications is a stronger leg than one guide.

**One claim refuted, now across three documents.** The labels *"single-possibility probing"* and *"multi-possibility probing"* appear **nowhere** in the 1999 guide, **nowhere** in the 2012 guide, and **nowhere** in Elaine McColl's published review of the 2005 Sage book (*Quality of Life Research*, supplied 2026-09-01 — a **secondary** source, recorded as such). The review does confirm the book contains a section titled *"The Intricacies of Verbal Probing"*, so the book remains the only place the labels could live. **The substance is verbatim twice over; the terminology remains unattested anywhere.**

### Beyer and Holtzblatt, *Contextual Design* — R9, and a third voice on R10

The **Interpretation** principle, one of four (context, partnership, interpretation, focus):

> *"If the data that matters is the interpretation, we must have a way to ensure it is correct, and we can only do that by **sharing it with the customer**. We fail in the entire purpose of working with customers if we do not share and validate our interpretations of their work — the most important data we bring back would not be validated."*

Confirmation is continuous and per-interpretation, which is R9, with R31 as the terminal half.

**They also answer the acquiescence objection R10 records as an open disagreement**, and they answer it against Fitzpatrick:

> *"Will customers be prone to agree with whatever you say? **In fact, it is quite hard to get people in the middle of doing work to agree with a wrong interpretation.** … The statement that doesn't fit is like an itch, and they poke and fidget with it until they've rephrased it so it represents their thought well: 'It's like a traveling office,' you say… 'Well — like a traveling desk,' he responds."*

The condition is doing the work at the time. That is a real constraint on transfer here, where the author is reasoning about software not yet built rather than being observed mid-task — so this strengthens R9 more than it settles R10.

### Gilb, *Competitive Engineering* (2005) — R16 and R17

R16, verbatim:

> *"**Meter:** A practical method for measuring and testing a scalar attribute level, on a defined Scale."*

R17 — **and the parameter names this project had been citing were wrong.** Planguage's two levels are:

> *"**Fail:** a level needed to avoid a system failure of some kind"* — classed as a **constraint**

> *"**Goal:** A future required level under defined [time, place, event] conditions, which has to be achieved to claim success in meeting a performance attribute requirement."* — classed as a **target**

Not `Must` and `Plan`, which was asserted from a mirror. Gilb also orders them — *"Given the same set of qualifiers, constraints are of higher priority than targets"* — which R17 does not yet encode.

### IEEE adoption of ISO/IEC 15026-3 (2013) — corroborates R3

12207's own delegation target for the taxonomy, obtained. It does not supply a category list the way IMDRF does; it requires the assignment be earned:

> *"Risk analysis and/or evaluation shall be performed: a) Initially, **before the first assignment** of an agreed upon or approved system or product integrity level."*

Same principle as IMDRF §7.1 — the level is derived, not declared — reached from the general case rather than the medical one. **R3's open question is answerable now:** IMDRF supplies a taxonomy and 15026-3 supplies the obligation to derive one, so the two are complementary rather than alternatives.

### ISO/IEC/IEEE 24748-2:2024 — scanned, and it adds nothing

Supplied and read against the set on 2026-09-01. **The scan is the finding: it corroborates and adds no requirement.** It is guidance on applying 15288 within an organisation, and refers out to ISO/IEC/IEEE 15288:2023 — not in hand — for everything normative, including its tailoring requirements at Annex A.

Measured emptiness on this set's weak points: **zero** hits for any cap on elicitation effort (R7), **zero** for a need arriving unframed (R1), and **zero** on what to do when the stakeholder is absent (R33, still the set's lowest-rung source). Its 23 "tailoring" occurrences are about which of 15288's processes apply to a project, not about declining a request, so they do not reach R2.

Two sentences are worth keeping, both corroboration:

> *"upward and downward traceability (or completeness and consistency checks) between the stakeholder needs and stakeholder requirements should be performed to confirm that **no requirements have been omitted or added without accountability**."*

That is R11 and R37 together — every requirement traceable to a need, checked across the set rather than per item.

> *"The resulting set of technical requirements should be checked for **non-singular requirements containing multiple parts, which should then be decomposed** into individual (singular) requirements."*

R15, and worth recording because it names the exact defect this session hit twice: R4 and R9 were each a conjunction whose second half nothing tested, and both had to be split — into R30 and R31 — after the sourcing screen caught one of them. A standard treats that as a routine set-level check. Here it was found by accident.

______________________________________________________________________

## Unanchored

Named rather than stretched onto a near-miss, per the method's own rule.

**"Reduce what the author has to supervise"** — the success criterion the phase is designed against — has **no anchor in any tradition surveyed**. No requirements-engineering standard, no discovery practice and no agent toolchain measures itself by the practitioner's attention. It remains a stated preference with no external support.

## Method and limits

Six corpora, read by isolated agents with adversarial verification on the load-bearing claims. 29148 and 12207 were subsequently read directly from the primary PDFs, which corrected four claims the secondary reproductions had compressed or dropped.

**Not reached:** IEEE 830-1998 in full; RIBA Plan of Work; ISO 26262 and ARP4754A; ISO/IEC 15026-3; IEC 62304; FDA's General Wellness guidance. Planguage was read through a mirror rather than the source publication, and so was INCOSE's Guide for Writing Requirements — **obtained 2026-09-01 and quote-verified locally, but from a university mirror rather than from INCOSE.** **Resolved 2026-09-01:** Fitzpatrick, Willis, Beyer and Holtzblatt, Gilb and ISO/IEC 15026-3 were all supplied by the author and read — see the section above. Still not read directly: **Willis, G. (2005), *Cognitive Interviewing: A Tool for Improving Questionnaire Design*, Sage** — named by the 2012 guide's own opening note as the book it became. It is the likely home of the "single-possibility / multi-possibility" terminology, but that is a **guess**: all that is established is that the labels are absent from the guide. Nothing in the requirement set depends on it, since Willis 2012 and Pew both carry the substance.

**Contamination risk, disclosed:** the agents in the earlier sweeps were given a shared guard block naming the other candidates and, in one case, an explicit statement of which requirements were believed unmet. That is priming, and it is the failure `neuroarxiv` names — *"a read that has seen other papers' abstracts starts summarizing the SET"*. The findings above from those sweeps should be weighted accordingly; the two standards, read directly and last, are not affected.
