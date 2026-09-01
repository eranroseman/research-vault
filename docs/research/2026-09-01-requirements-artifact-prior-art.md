# Prior art: what a requirement must carry, and what a requirements document needs

Research note, 2026-09-01. Feeds the requirements for `writing-requirements`, the pre-spec phase — see `docs/superpowers/requirements/2026-09-01-writing-requirements.md`.

**Question asked:** how is this class of problem — turning a need into a written, verified statement of what and why — solved well elsewhere? Patterns, not vendors. A pattern costs nothing to take, so nothing here needs a disposition.

**Why it was run.** Six agent-skill designs had converged on roughly six fields (goal, problem, success, scope, out-of-scope, open questions), but all six were written in the same two-year window by people in the same ecosystem, so the convergence could be imitation rather than discovery. This tested it against traditions that predate them.

**Result, stated up front:** the convergence is **rediscovery, and lossy**. The Volere requirements shell had the per-requirement shape in the mid-1990s, including two fields all six modern designs dropped.

---

## Volere requirements shell — the strongest single finding

Suzanne and James Robertson, Atlantic Systems Guild. Shell fields read from Edition 11 (February 2006); document template contents from Edition 16 (2012).

The shell is a **per-requirement card**. Its fields, with the glosses printed on the card:

| Field | Gloss |
|---|---|
| Requirement # | Unique id |
| Event/use case #'s | List of events / use cases that need this requirement |
| Requirement Type | The type from the template |
| **Description** | A one sentence statement of the intention of the requirement |
| **Rationale** | A justification of the requirement |
| **Originator** | The person who raised this requirement |
| **Fit Criterion** | A measurement of the requirement such that it is possible to test if the solution matches the original requirement |
| Customer Satisfaction | Degree of stakeholder happiness if implemented. 1 = uninterested to 5 = extremely pleased |
| Customer Dissatisfaction | Measure of unhappiness if not part of the final product. 1 = hardly matters to 5 = extremely displeased |
| Priority | A rating of the customer value |
| Conflicts | Other requirements that cannot be implemented if this one is |
| Supporting Materials | Pointer to documents that illustrate and explain this requirement |
| History | Creation, changes |

**Why it fits.** Description + Rationale + Originator + Fit Criterion is requirement, why, source and check — on one card. `Fit Criterion` is the field every modern candidate drops, and it is the one a downstream planning phase needs in order to write a test. `Originator` is the provenance tag six separate agent skills were each solving independently.

**And the document has a section for sourcing.** Volere's 27-section template, in five groups, includes *Project Drivers* (Purpose, Stakeholders), *Project Constraints* (Mandated Constraints, Naming Conventions, **Relevant Facts and Assumptions**), *Functional Requirements* (Scope of the Work, Scope of the Product, Functional Requirements), eight classes of non-functional requirement, and *Project Issues* — including **18. Open Issues** and **19. Off-the-Shelf Solutions**.

So build-or-buy is a numbered section of a requirements specification, kept separate from the requirements themselves.

**Caveat.** The shell's `Priority`, `Customer Satisfaction` and `Customer Dissatisfaction` fields are planning apparatus for an organisation choosing what to build first. They do not transfer to a one-person setting and are not taken.

---

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

---

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

---

## Syntax traditions

**EARS** (Mavin et al., Rolls-Royce). A sentence grammar: *"While \<optional pre-condition\>, when \<optional trigger\>, the \<system name\> shall \<system response\>."* Fits the singularity and unambiguity requirements. **Silent on** document structure, on rationale, on source, and on quantification — it says when a sentence is well-formed, never when a specification is done.

**Planguage** (Tom Gilb). Quantifies a quality requirement with `Scale` and `Meter`, and separates the failure threshold from the target: **`Must`** is the level below which the requirement fails, **`Plan`** the level aimed at. A quality with no scale of measure is not a requirement. This is the two-level threshold, thirty years before the "guardrail metric" appeared in agent PRD templates.

*Caveat, marked unverified:* Planguage was read through a mirror site rather than Gilb's own publication.

---

## The agile lineage dissents from the artifact

Recorded because it argues against the phase existing, and the argument should travel.

Jeffries: *"The card is a token representing the requirement"* — the requirement deliberately does not live in a document, and validation is a demonstration at the **end** of implementation rather than a confirmation before it. Card, Conversation, Confirmation, where confirmation is the acceptance test.

**Why it does not bind here.** The argument is correct about a world where the document substituted for conversation with a distant customer and cost weeks to write. Here the customer is in the room, the document exists because an agent cannot have the conversation, and it costs a session. The conditions that made the argument right do not hold.

Mattpocock documents the related failure for his own template: *"The template leans hard on user stories, which is the wrong shape for architectural work: you end up writing stories nobody asked for around decisions that are really about interfaces and invariants."*

---

## Requirements defects

Femmer, Méndez Fernández, Wagner and Eder, "Rapid Quality Assurance with Requirements Smells". The smell catalogue maps onto 29148 5.2.7 and adds detection tooling. **Recorded as secondary to the standard**: 5.2.7 is the older and more authoritative statement of the same list, and it carries two categories the smells literature does not.

---

## Interview technique

**The guess-attached question is a real technique, and the agent-skill rendering of it is a mutation.** Beyer and Holtzblatt's contextual-inquiry **Interpretation** principle has the interviewer state their reading back — but the guess is **backward-looking**: it reflects meaning already expressed, and is delivered as a **statement**, not attached to an unanswered question.

Where a hypothesis must precede an answer, Willis names **single-possibility probing** as the biasing form and **multi-possibility probing** as the remedy: offer the plausible alternatives, not one. Pew documents acquiescence bias, worse with an interviewer present — and an agent asking questions is an interviewer present — plus order effects.

**Restating for confirmation is standard and has two names**: contextual inquiry's *Interpretation*, and qualitative research's *member checking*. In both traditions it is **continuous and in the moment**, not concentrated into one terminal restatement.

**Anchor questions in specific past events**, not opinions, generalities or predictions. Three independent primaries converge; the strongest single agreement in the discovery corpus.

**Nobody caps question count.** Every practice caps something adjacent instead — learning goals per person-type, session length, question density. One quantified rule exists, from motivational interviewing: reflections must outnumber questions, and stacked questions are forbidden.

---

## Unanchored

Named rather than stretched onto a near-miss, per the method's own rule.

**"Reduce what the author has to supervise"** — the success criterion the phase is designed against — has **no anchor in any tradition surveyed**. No requirements-engineering standard, no discovery practice and no agent toolchain measures itself by the practitioner's attention. It remains a stated preference with no external support.

## Method and limits

Six corpora, read by isolated agents with adversarial verification on the load-bearing claims. 29148 and 12207 were subsequently read directly from the primary PDFs, which corrected four claims the secondary reproductions had compressed or dropped.

**Not reached:** IEEE 830-1998 in full; INCOSE's Guide for Writing Requirements; RIBA Plan of Work; ISO 26262 and ARP4754A. Planguage was read through a mirror rather than the source publication.

**Contamination risk, disclosed:** the agents in the earlier sweeps were given a shared guard block naming the other candidates and, in one case, an explicit statement of which requirements were believed unmet. That is priming, and it is the failure `neuroarxiv` names — *"a read that has seen other papers' abstracts starts summarizing the SET"*. The findings above from those sweeps should be weighted accordingly; the two standards, read directly and last, are not affected.
