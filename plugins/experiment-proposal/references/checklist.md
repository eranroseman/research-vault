# Checklist: the items of an experiment proposal

Derived from the Done-when lists of *How to Write an Experiment Project Proposal* (the guide), Backchat commit `98b978fb74b7480c9967ceb2a1100e4560081af5`, file `docs/guides/How to Write an Experiment Project Proposal.md`; the research-vault copy of the guide is `docs/guides/experiment-proposal-guide.md`. Judged by the lens, the course assignment the proposal is written for (`docs/superpowers/specs/2026-10-14-experiment-proposal-v2-design.md`, Goal): what the lens does not ask for is not checked. The deviations below are built in. The skills read this file and never the guide.

## How to read an item

Each item is one line: `- **ID** (kind; scope; depends on IDs) holds-when text`.

- **ID** is `step.number`; the steps are the guide's: 1 fit and ethics, 2 plan, 3 document, 4 introduction, 5 literature review, 6 questions and hypotheses, 7 design, 8 participants, 9 materials, 10 procedure, 12 appendix, 13 review and defend; step 11, planned analysis, is not checked (see Deviations).
- **kind** is `draft-checked` (the draft can show it: `review` passes it only with a quoted passage and its location), `attested` (it concerns the process, not the text: `review` records the user's confirmation) or `defend-stage` (research-grill's; `review` never checks it).
- **scope** is `design-tree` (`design` elicits it, in rounds ordered by `depends on`) or `review-only` (checked against the draft only).
- **depends on** lists the items that must be settled before this one is asked or checked; `none` when there are none. For `design`'s rounds only `design-tree` dependencies block a question.
- Cite an item anywhere as `item 7.4`, or several as `items 7.1, 7.2 and 7.5`.

## Deviations from the guide

- Step 11, planned analysis, is not checked: the lens's section list has no Planned Analysis section, and the guide's own rule applies, that the template's section list overrides its typical sections. Step 2's "test for each hypothesis" is dropped from item 2.1 with it, and no power analysis is run: item 8.5 takes the guide's alternative, a count justified by similar experiments and a stated reason.
- The lens's mechanics are items the draft can show: the section list and order (item 3.2), the word bounds (item 13.5), the reference count (item 5.1), the bullet list of contributions (item 4.3) and the consent form's supervision sentence (item 12.3); item 3.1 records the template's values for them, with the course's values as defaults.
- The plugin's `lit-search` skill replaces step 5's search tips; item 5.2 is attested.
- research-grill's defend stage replaces "present to a critical listener" (item 13.2), and its written record serves the feedback item (item 13.3); `review` checks neither and hands off to the defend stage.
- Additions: the six substance tests (items 13.6 to 13.11), restated in our own words from hutzelmann's proposal-supervise skill (MIT).
- Three ideas restated from scdenney's research-grill (CC BY-NC 4.0, no text copied) shape `design`, not this list: the "why this matters" line, provisional answers, and a written record.

## Step 1: fit, ethics and data

- **1.1** (draft-checked; design-tree; depends on none) The research question is one sentence asking whether changing the independent variable, with its levels named, causes a change in the dependent variable; later steps may add variables.
- **1.2** (draft-checked; design-tree; depends on 1.1) The ethics route is stated: an existing approval that covers the study, or the body that decides whether the study needs review, what that body requires, and how long its review takes.
- **1.3** (draft-checked; design-tree; depends on 1.1) The data plan gives the reason for each kind of identifiable data collected (data minimization), names who will have access, and sets how long the raw data are kept.

## Step 2: plan

- **2.1** (draft-checked; review-only; depends on 7.1, 7.6, 8.5, 9.1, 10.2) Every Method value is decided or marked as one the pilot will settle: each independent variable with its levels and its within- or between-subjects label, each dependent variable with its unit, the number of participants, the materials, and the session phases.
- **2.2** (draft-checked; design-tree; depends on 7.3) The conditions each participant sees are counted, with the number of trials per condition, and the session estimate, from welcome to debriefing with consent, questionnaires and moving between tasks included, is as short as the design allows and fits the time available.
- **2.3** (draft-checked; design-tree; depends on 2.2) The pilot plan says how many people take part, what the pilot will refine, and whether its data will be reported; pilot data stay out of the main sample unless the pilot runs exactly as the proposal describes.
- **2.4** (draft-checked; design-tree; depends on 2.3) A timeline names what each later phase delivers (pilot, data collection, analysis, write-up) and when, within the time available; the proposal includes it when the template asks for one.
- **2.5** (draft-checked; design-tree; depends on 2.4) Each expected challenge, such as too few sign-ups, a manipulation that fails in the pilot, or running short of time, has a planned response stated in the section it affects.

## Step 3: document

- **3.1** (attested; review-only; depends on none) The template's requirements are identified and recorded: its section list and order, its word bounds and whether references and appendices count toward them, its reference bounds, its citation style, and the supervising instructor's name; the course's values are the defaults when the template leaves one unsaid.
- **3.2** (draft-checked; review-only; depends on 3.1) The draft has a heading for every section the template lists, in the template's order, with Design separate from Procedure.
- **3.3** (draft-checked; review-only; depends on 3.2) The draft follows the conventions throughout: a short, to-the-point title; an abstract, if there is one, under 150 words or the template's limit; the future tense; every borrowed idea cited and every cited work listed under References in the required style; "statistically significant" written in full; and every Method section replicable from its own text.

## Step 4: introduction

- **4.1** (draft-checked; review-only; depends on 1.1) An opening overview names what will be compared, what will be measured, the task, and who takes part.
- **4.2** (draft-checked; review-only; depends on 5.1) The section states the motivation (why this project), the problem, and its significance with citations.
- **4.3** (draft-checked; review-only; depends on 4.2) The section lists the contributions as bullets, each saying what a reader will get from the final report.
- **4.4** (draft-checked; review-only; depends on 1.1) The section says why an experiment, rather than a survey or observation, answers the question.
- **4.5** (draft-checked; review-only; depends on 3.2) The section previews the rest of the proposal.

## Step 5: literature review

- **5.1** (draft-checked; review-only; depends on none) The review cites work that motivates the problem, work that justifies the approach, and similar studies, and the reference list holds the number of references the template asks for.
- **5.2** (attested; review-only; depends on 5.1) Snowballing from at least one recent key article has stopped turning up new relevant work; the `lit-search` skill's stop rule is the usual evidence.
- **5.3** (draft-checked; review-only; depends on 5.1) The review ends by stating the gap and how the study fills it.

## Step 6: research questions and hypotheses

- **6.1** (draft-checked; design-tree; depends on 1.1, 5.1) The section states a hypothesis wherever the direction of the independent variable's effect on the dependent variable can be predicted, and a research question where it cannot.
- **6.2** (draft-checked; design-tree; depends on 6.1) Each hypothesis names its independent and dependent variables and the predicted direction, cites the Literature Review sources that justify that direction, and can be tested against a null hypothesis of no difference.
- **6.3** (draft-checked; review-only; depends on 6.2, 7.1) Each hypothesis is scoped to the levels tested: a two-level experiment supports claims about those two levels only.
- **6.4** (draft-checked; review-only; depends on 6.1) Each research question names the independent and dependent variables it concerns.
- **6.5** (draft-checked; design-tree; depends on 6.1) Each "it might depend" idea is stated as an interaction hypothesis that names the interacting variables.
- **6.6** (draft-checked; review-only; depends on 6.2) Each hypothesis's possible outcomes, including a non-significant one, are listed, and each is interpretable.

## Step 7: design

- **7.1** (draft-checked; design-tree; depends on 1.1) Each independent variable has an operational definition, named levels in a range wide enough to show an effect and realistic enough to matter in practice, justified by the literature or the pilot, and a within- or between-subjects label with a reason specific to this experiment.
- **7.2** (draft-checked; design-tree; depends on 7.1) Each within-subjects variable has carry-over expected to be symmetric; a variable with asymmetric carry-over, such as a tutorial that cannot be unseen, is between subjects.
- **7.3** (draft-checked; design-tree; depends on 7.1, 6.5) The overall design is named (for example, 2 × 3 × 3 mixed factorial); every interaction hypothesis has its variables crossed factorially, and every variable on which participants are asked which condition they prefer is within subjects.
- **7.4** (draft-checked; design-tree; depends on 7.1) Each between-subjects variable has a random assignment procedure that names a truly random source, such as a random-number generator, a shuffled list, a coin, or a die; with no between-subjects variable, the section says so.
- **7.5** (draft-checked; design-tree; depends on 7.2) The order of within-subjects conditions is counterbalanced (with a Latin square for many conditions) or randomized by the same kind of procedure within constraints such as equal numbers per condition.
- **7.6** (draft-checked; design-tree; depends on 1.1) Each dependent variable has an operational definition with its unit, how it is recorded, a reliability statement, a construct-validity statement, and its measurement scale; each speed measure is paired with an accuracy measure, and the two will be reported together.
- **7.7** (draft-checked; design-tree; depends on 7.1) Each control variable has an operational definition (how it is set or checked) and a justification that weighs the internal validity it buys against the external validity it costs.
- **7.8** (draft-checked; design-tree; depends on 7.1) The random variables are listed.
- **7.9** (draft-checked; design-tree; depends on 7.1) Each confound, including history, maturation and instrumentation, is listed with how it will be prevented.

## Step 8: participants

- **8.1** (draft-checked; review-only; depends on 2.3, 8.3) Recruitment, screening and the number describe the full experiment; if the pilot sample differs, one sentence says how, and the section says whether the pilot's data will be reported.
- **8.2** (draft-checked; review-only; depends on 8.3) The recruitment method is stated, with how candidates can decline without consequence.
- **8.3** (draft-checked; design-tree; depends on 7.7) Each eligibility criterion is listed with how it will be screened, and none selects people for an extreme score on a measure of the behaviour studied.
- **8.4** (draft-checked; review-only; depends on 8.3) The section says whether the sample is randomly selected or a convenience sample, and names the population the results will cautiously describe.
- **8.5** (draft-checked; design-tree; depends on 7.3, 7.6) The number is justified by similar experiments and a stated reason for the count, says how the pilot will refine it, and is pre-specified.
- **8.8** (draft-checked; review-only; depends on 7.5, 8.5) The between-subjects groups, if any, are equal in size, and each group (the whole sample, in a within-subjects design) is a multiple of the number of counterbalanced orders, if any, so every group and order is used equally often.
- **8.9** (draft-checked; review-only; depends on 8.5) The number of extras for people who do not show up or do not fit the profile is stated.

## Step 9: materials

- **9.1** (draft-checked; review-only; depends on 7.1) Every item participants interact with is listed: each piece of hardware, each program with what it presents and records, and each questionnaire.
- **9.2** (draft-checked; review-only; depends on 7.6, 9.1) Every dependent variable in the Design section has an item here that records it.
- **9.3** (draft-checked; review-only; depends on 9.1) Each program written for the study logs every trial automatically, so nothing is copied by hand; its logged fields are listed; and the section says how it will be confirmed to run and log correctly before anyone uses it.
- **9.4** (draft-checked; review-only; depends on 9.1) Each questionnaire is a named standard instrument, or a custom one with the reason no standard one fits, and every self-report measure is described as what participants reported.

## Step 10: procedure

- **10.1** (draft-checked; review-only; depends on 9.1) The section names where sessions run and whether participants are tested alone or in groups.
- **10.2** (draft-checked; review-only; depends on 2.2, 9.1) A session is described phase by phase in order (welcome, consent, instructions, tasks, questionnaires, debriefing), with the number of trials per condition and an estimated duration for each phase; the durations sum to the session estimate.
- **10.3** (draft-checked; review-only; depends on 10.2) Every Materials item appears at the point in the session where it is used.
- **10.4** (draft-checked; review-only; depends on 10.2) The section says how every participant hears the same instructions and how cues that could differ between conditions are held constant.
- **10.5** (draft-checked; review-only; depends on 10.2) The section says what happens if the experimenter falls ill or the equipment breaks down.

## Step 12: appendix

- **12.1** (draft-checked; review-only; depends on 1.2, 9.4, 10.2) The Appendix holds every recruiting material, such as flyers; the informed consent form; the verbatim script; every questionnaire named in the Materials section; and the ethics-review documentation: an approval letter, a completed review form, or a statement that the study falls under an existing approval.
- **12.2** (draft-checked; review-only; depends on 12.1) The section that uses each Appendix item refers to it.
- **12.3** (draft-checked; review-only; depends on 1.3, 2.2, 12.1) The consent form and the script cover every disclosure: who runs the study, their affiliation and, for a student, the supervisor; why the study is run; its purpose, expected duration and procedures; the right to decline and to withdraw after starting, and the consequences of either; foreseeable risks or discomfort, benefits and incentives; limits of confidentiality, who will see the data and results, and how long the raw data are kept; and a named contact for questions about the research and one for questions about participants' rights. The stated duration matches the session estimate, and the consent form states that the study is under the supervision of the named instructor.
- **12.4** (draft-checked; review-only; depends on 12.1) The consent form says how consent is recorded.
- **12.5** (draft-checked; review-only; depends on 12.1) The script includes a point where participants can ask questions.
- **12.6** (draft-checked; review-only; depends on 8.3, 12.1) Every demographic question serves a need stated in the Participants section (data minimization) and has space for its answer.

## Step 13: review and defend

- **13.1** (attested; review-only; depends on 13.5) The proposal has been reviewed against the seven reader questions (importance, credibility, ethics, novelty, external validity, assumptions, readability) and revised where it fell short.
- **13.2** (defend-stage; review-only; depends on 13.5) The experiment has been presented at least once to a critical listener; research-grill's defend stage is that listener, and `review` hands off to it instead of checking this item.
- **13.3** (defend-stage; review-only; depends on 13.2) Each piece of feedback, and each question that could not be answered, is recorded with what was done about it, and every revision is in the draft; research-grill's written record serves this item, and `review` does not check it.
- **13.4** (attested; review-only; depends on 7.1) The reason for every choice in the Design section can be given; the brief's rationale entries are the record.
- **13.5** (draft-checked; review-only; depends on 3.3) The draft to be submitted satisfies every item of steps 1 to 12, uses the required template with its section list in order, describes the full experiment rather than the pilot, follows the step 3 conventions (item 3.3) throughout, and is within the word bounds excluding references and appendices.
- **13.6** (draft-checked; review-only; depends on 4.3, 5.3) Delta: the proposal states precisely what the study adds beyond the work it cites, what it confirms, refutes or extends; contributions that read as a feature list or restate the field fail.
- **13.7** (draft-checked; review-only; depends on 6.2, 6.6) Falsifiability: every hypothesis and research question can come out negative; a question whose every conceivable outcome counts as success fails.
- **13.8** (draft-checked; review-only; depends on 4.1, 6.2) Swap: the overview, the hypotheses and the contributions could not equally describe ten other studies in the area; text that stays plausible after swapping the technique, the task or the population fails, and so does a named device, system or domain the study does not depend on.
- **13.9** (draft-checked; review-only; depends on 3.3) Necessity: every sentence, citation and technical term serves a hypothesis, the gap or the method; material that is true and well-sourced still fails if removing it would not weaken the argument.
- **13.10** (draft-checked; review-only; depends on 7.6) Method fit: the Design, Materials and Procedure sections concretely answer each hypothesis and research question; method prose that never touches them is boilerplate and fails.
- **13.11** (draft-checked; review-only; depends on 2.4) Executability: the proposal names the population, the task and the apparatus, states how each dependent variable is measured, fits the time available with its timeline (item 2.4), and makes clear what the author would do first; a choice the pilot can settle without changing a hypothesis does not fail it.
