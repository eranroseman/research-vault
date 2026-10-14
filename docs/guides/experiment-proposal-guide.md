# How to Write an Experiment Project Proposal

*Master copy since 2026-10-14; moved here from the Backchat repository at its commit 98b978f, whose copy is to be deleted after this branch merges. The experiment-proposal plugin's checklist (`plugins/experiment-proposal/references/checklist.md`) derives from the Done-when lists below; the plugin's skills read the checklist, never this file.*

An **experiment proposal** describes the full experiment you plan to run with human participants; this guide takes you through planning that experiment and writing the proposal in 13 steps. Each step ends with a **Done when:** list, and the step is finished when every item holds. A running example, a study comparing a mouse and a trackball for selecting targets on a screen, shows parts of filled-in sections; replace its participants, values, and hypothesis directions with ones your literature review or pilot justifies. Use the guide for experiments, such as HCI studies that pit a new interaction technique or application against the ones people already use, or set two interaction styles head to head; archival studies, such as systematic literature reviews, follow a different structure.

## The Process: Planning the Experiment and Writing the Proposal

### 1. Before you write: check that an experiment fits, and find out what ethics review requires

- The independent variable is the circumstance you will change; the dependent variable is the behavior you will measure.
- *Running example:* "Is target selection faster with a mouse or a trackball?" changes the device (two levels: mouse and trackball) and measures movement time.
- Check that an experiment fits your question. Only a well-controlled experiment can show cause; correlational observation, surveys, and archival research cannot.
- Research with human participants usually needs approval from an institutional review board (IRB) or a similar body before it starts, and review can take weeks, so start early, while the plan can still change. The review body, not you, decides whether your study is exempt.
- **Data minimization** means collecting identifiable data only where the study needs it; such data include names linked to performance data and recordings that show faces, voices, or personal screens. Confidentiality is one of a review board's main concerns, and minimized data has less to leak. Raw data — the individual measurements before analysis combines them — are usually kept unedited and de-identified for at least five years, unless your ethics review sets a different period.
- **Done when:**
  - The question is one sentence asking whether changing the independent variable (with its levels) causes a change in the dependent variable; later steps may add variables.
  - You have identified an existing approval that covers the study, or the body that decides whether it needs review, what that body requires, and how long its review takes.
  - The proposal's data plan gives the reason for each kind of identifiable data collected (data minimization), names who will have access, and sets how long the raw data are kept.

### 2. Plan the whole experiment before you draft

- Treat the proposal as the front half of the eventual paper: everything from the introduction through the method.
- Each condition a participant sees, one combination of levels, lengthens the session. A **session estimate** is the length of a whole session from welcome to debriefing (explaining the study and thanking the participant), including consent, questionnaires, and moving between tasks. Short sessions tire participants less, and a single session avoids no-shows at return visits.
- Plan a pilot, a small rehearsal of the full experiment: run the procedure on a few people, note what breaks or confuses them, and use the lessons to refine the levels of each independent variable, the script, the timings, and the planned number of participants. Because a pilot's results are not published, its rules can bend: friends can take part, you can serve as a participant yourself, and levels can change midway. To report the pilot's data, run it exactly as the proposal describes.
- **Done when:**
  - Every Method and Planned Analysis value is decided or marked as one the pilot will settle: each independent variable with its levels and within- or between-subjects label, each dependent variable with its unit, the number of participants, the materials, the session phases, and the test for each hypothesis.
  - The conditions each participant sees are counted, and the session estimate, overhead included, is as short as the design allows and fits the time available.
  - The pilot plan says how many people take part, what the pilot will refine, and whether its data will be reported.
  - A timeline names what each later phase delivers (pilot, data collection, analysis, write-up) and when, within the time available; the proposal includes it when the template asks for one.
  - Each challenge you expect, such as too few sign-ups, a manipulation that fails in the pilot, or running short of time, has a planned response stated in the section it affects.

### 3. Set up the document

- Your program, supervisor, or target venue may set a template, length limit, citation style, and section list; these override the typical sections below. Appendices and references usually do not count toward a length limit.
- The typical sections of an experiment proposal are: Introduction; Literature Review; Research Questions or Hypotheses; Participants, Materials, Procedure, and Design, which together form the Method; Planned Analysis; References; and an Appendix. A separate Design section keeps the variables in readers' view. The steps below draft Design right after the hypotheses, ahead of its usual place in the document, because the variables decide who you recruit, what materials you need, and how sessions run.
- Follow these conventions throughout the proposal:
  - Give the proposal a short, to-the-point title that tells the reader what to expect.
  - If your proposal has an abstract, keep it under 150 words, or within your template's limit.
  - Write in the future tense.
  - Cite every idea you take, in any section, quoted or paraphrased; an uncited idea is plagiarism even when the omission is unintentional. List every cited work under References in the required citation style.
  - Write "statistically significant" in full.
  - Make every Method section **replicable**: another researcher could reproduce it from that section alone.
- **Done when:**
  - The template, length limit, citation style, and section list are identified, along with whether appendices and references count toward the limit; with no template, the typical sections are chosen.
  - The draft has a heading for every required section, in the template's order or else the typical order (Planned Analysis may instead close the Method), with Design separate from Procedure.

### 4. Write the Introduction section

- *Running example:* the overview might read, "We will compare movement time and error rate with a mouse and a trackball when right-handed young adults select targets at three distances and three sizes."
- **Done when:**
  - An opening overview names what you will compare, what you will measure, the task, and who takes part.
  - The section states the problem and argues its significance with citations.
  - The section lists your contributions as bullets, each saying what a reader will get from the final paper.
  - The section says why an experiment, rather than a survey or observation, answers the question.
  - The section previews the rest of the proposal.

### 5. Write the Literature Review section

- Start from papers you already know in the area and search Google Scholar; your library can usually get you articles that sit behind a paywall.
- Check completeness by snowballing: work backward through a recent key article's references and forward through later papers that cite it (Google Scholar's "Cited by" link).
- Prefer current sources: journal articles are the most current formal source, while review articles and books lag years behind. Read each paper three times: to get the gist, to understand it, and to critique it.
- Build the review toward the gap your study fills. A gap is a deficiency in past research, such as a topic not yet studied with a particular group or a finding not yet replicated with new samples or sites. You are unlikely to find work that matches your project exactly, and that is good: the gap leaves room for your contribution. Use the related-work sections of well-written papers you have read as models for organizing yours.
- Use the literature to justify later decisions: the direction of each hypothesis and the levels of each independent variable.
- **Done when:**
  - The review cites work that motivates the problem, work that justifies your approach, and similar studies.
  - Snowballing from at least one recent key article has stopped turning up new relevant work.
  - The review ends by stating the gap and how your study fills it.

### 6. Write the Research Questions or Hypotheses section

- If your idea sounds like "it might depend," you probably have an interaction hypothesis, which needs a factorial design ([if factorial designs are unfamiliar, read design types](#background-design-types-and-counterbalancing)).
- *Running example:*
  - H1: Mean movement time will be shorter with the mouse than with the trackball.
  - H2: Error rate will be lower with the mouse than with the trackball.
  - H3: The mouse's movement-time advantage over the trackball will be larger for smaller targets (an interaction between device and target size).
- **Done when:**
  - The section states hypotheses where you can predict how the independent variable will affect the dependent variable, and research questions where you are unsure what you will find.
  - Each hypothesis names its independent and dependent variables and the predicted direction, cites the Literature Review sources that justify that direction, and can be tested against a null hypothesis of no difference.
  - Each hypothesis is scoped to the levels you test: a two-level experiment supports claims about those two levels only.
  - Each research question names the independent and dependent variables it concerns.
  - Each "it might depend" idea is stated as an interaction hypothesis that names the interacting variables.
  - You have listed each hypothesis's possible outcomes, including a non-significant one, and can interpret each.

### 7. Write the Design section

- An operational definition gives the operations anyone must carry out to set up or measure a variable identically, like a recipe ([if independent, dependent, control, or random variables or confounds are unfamiliar, read their definitions](#background-variables-and-confounds)). Vague constructs such as "visual complexity" or "stress" need especially careful definitions.
- Range of levels: for network delay, 0 versus 20 ms may be too narrow to show anything, while 0 ms versus 10 seconds is a "sledgehammer" range that guarantees a difference of no practical use.
- A within-subjects variable risks **carry-over**: exposure to one condition changes behavior in the next. Counterbalancing cancels carry-over only when it is symmetric, when condition A changes behavior in B as much as B changes it in A ([to weigh within against between subjects, or to build a Latin square for many conditions, read design types and counterbalancing](#background-design-types-and-counterbalancing)).
- Control buys precision (internal validity) and makes the study easier to replicate, but too much control costs **external validity** (how far results generalize beyond your sample and setting): a quiet, comfortable lab may not match real conditions of use.
- Three confounds arise over time:
  - History: outside events affect one condition more than another; collect data for all conditions at about the same time.
  - Maturation: participants change during the study; keep the study short.
  - Instrumentation: the measuring tools change midway; freeze the study software and other measuring tools before data collection starts.
- A dependent variable's reliability asks whether you would get the same result again, and whether software, a stopwatch, or video does the timing; its **construct validity** asks whether it measures what you intend. People trade speed for accuracy (the speed–accuracy tradeoff), so a speed measure alone can mislead.
- Measurement scales: times and error counts are interval or ratio data, rankings are ordinal, and categories are nominal (the test table's Categorical column).
- *Running example:*
  - **Independent variables:**
    - Device: mouse or trackball; between subjects, each participant assigned to one device from a randomly shuffled list that keeps the groups equal.
    - Distance: 128, 256, and 512 pixels from the start point to the target center; within subjects.
    - Target size: 16, 32, and 64 pixels wide; within subjects.
    - Together: a 2 × 3 × 3 mixed factorial design, with device between subjects and distance and size within.
  - *Why keep device between subjects?* Participants who already use one device daily bring habits that may interfere with the other, while a few minutes on the new device barely disturb old habits; counterbalancing cannot fix this asymmetric carry-over. The costs are more participants and no way to ask which device participants prefer.
  - **Dependent variables:**
    - Movement time: milliseconds from the start of a trial to the click, timed by the study software. Ratio scale.
    - Error rate: the proportion of trials in which the click falls outside the target. Ratio scale.
  - **Control variables:** right-handed participants aged 18 to 22; the same display, software, task, room, and scripted instructions for everyone. The age and handedness restriction buys internal validity at the cost of external validity: the results may not describe left-handed users or older adults.
  - **Random variables:** individual skill, vision, mood, and anything else that varies by chance within the sample; the order of the nine distance-and-size combinations, randomized so each appears equally often.
  - **Confounds to watch for:** history and time of day, such as testing the mouse group in the morning and the trackball group in the afternoon (prevented by running both devices in the same weeks at similar times of day); letting participants choose their device (prevented by the random assignment above); using a different experimenter for each device (prevented by having one experimenter run every session); maturation (prevented by a single short session); instrumentation (prevented by freezing the study software before the first participant).
- **Done when:**
  - Each independent variable has an operational definition, named levels in a range wide enough to show an effect and realistic enough to matter in practice, justified by the literature or the pilot, and a within- or between-subjects label with a reason specific to this experiment.
  - Each within-subjects variable has carry-over you expect to be symmetric; one with asymmetric carry-over, such as a tutorial that cannot be unseen, is between subjects.
  - The overall design is named (for example, 2 × 3 × 3 mixed factorial); every interaction hypothesis from step 6 has its variables crossed factorially, and every variable on which you ask which condition participants prefer is within subjects.
  - Each between-subjects variable has a random assignment procedure that names a truly random source, such as a random-number generator, a shuffled list, a coin, or a die.
  - The order of within-subjects conditions is counterbalanced (with a Latin square for many conditions), or randomized by the same kind of procedure within constraints such as equal numbers per condition.
  - Each dependent variable has an operational definition with its unit, how it is recorded, a reliability statement, a construct-validity statement, and its measurement scale; each speed measure is paired with an accuracy measure, and the two will be reported together.
  - Each control variable has an operational definition (how it is set or checked, for example how handedness is determined) and a justification that weighs the internal validity it buys against the external validity it costs.
  - The random variables are listed.
  - Each confound, including history, maturation, and instrumentation, is listed with how you will prevent it.

### 8. Write the Participants section

- Voluntary participation is easy to undermine: someone taking part to meet an academic requirement may fear that declining will count against them, especially when participants are your own students or your classmates.
- Screening factors follow from your target population; typical ones are age, handedness, background with technology or software, disabilities, and health. People selected for an extreme score, such as the slowest users on a first trial, drift toward the average on retest even with no treatment (regression to the mean).
- HCI samples are rarely randomly selected; most are volunteers or convenience samples such as students, so results generalize only cautiously ([if random selection and random assignment blur, read the random procedures entry](#background-variables-and-confounds)).
- A power analysis calculates how many participants you need to detect an effect of a given size. Too small a sample leaves a study **underpowered**, one of the most frequent student mistakes, and too large a sample can make an unimportant effect statistically significant. To **pre-specify** a decision, such as this number or a planned test, is to fix it before you collect any real data.
- *Running example:* 24 right-handed adults aged 18 to 22, split evenly between the two devices (12 each), recruited with a flyer and screened for handedness and age, plus 4 extras for no-shows. They are a convenience sample, so the results describe right-handed young adults only cautiously.
- **Done when:**
  - Recruitment, screening, and the number describe the full experiment; if the pilot sample will differ, one sentence says how, and the section says whether the pilot's data will be reported.
  - The recruitment method is stated, with how candidates can decline without consequence.
  - Each eligibility criterion is listed with how you will screen for it, and none selects people for an extreme score on a measure of the behavior you will study.
  - The section says whether the sample is randomly selected or a convenience sample, and names the population the results will cautiously describe.
  - The number is justified by similar experiments and by a power analysis or a reason for omitting one; the section says how the pilot will refine it; and the number is pre-specified.
  - The between-subjects groups, if any, are equal in size, and each group (the whole sample, in a within-subjects design) is a multiple of the number of counterbalanced orders, if any, so every group and order is used equally often.
  - The number of extras for people who do not show up or do not fit the profile is stated.

### 9. Write the Materials section

- Standard questionnaires, such as the NASA Task Load Index (NASA TLX) for workload or the System Usability Scale (SUS) for usability, have usually been tested for construct validity; questions you invent have not. Answers to any questionnaire are self-reports that cannot be independently checked.
- *Running example:* a mouse and a trackball, each named by make and model; a computer with a 24-inch, 1920 × 1080 display, which fixes the physical size of the pixel distances and sizes above; a program that presents targets at three distances and three sizes and logs, for each trial, the condition, the movement time, and whether the click landed on the target; and a demographic questionnaire.
- **Done when:**
  - Every item participants interact with is listed: each piece of hardware, each program with what it presents and records, and each questionnaire.
  - Every dependent variable in the Design section has an item here that records it.
  - Each program written for the study logs every trial automatically, so nothing is copied by hand; its logged fields are listed; and the section says how you will confirm it runs and logs correctly before anyone uses it.
  - Each questionnaire is a named standard instrument, or a custom one with the reason no standard one fits, and every self-report measure is described as what participants reported.

### 10. Write the Procedure section

- Write a verbatim script, from welcome to debriefing, so every participant hears the same instructions. Read it in a neutral tone. Where experimenter cues could still differ between conditions, deliver instructions by recording or computer, or keep the experimenter blind to each participant's condition.
- *Running example:* each participant is tested alone in the same room. The experimenter welcomes the participant, obtains consent, and reads the script; after 10 practice trials with the assigned device, the participant completes 5 trials of each of the nine distance-and-size combinations in a randomized order, fills out the demographic questionnaire, and is debriefed.
- **Done when:**
  - The section names where sessions run and whether participants are tested alone or in groups.
  - A session is described phase by phase in order (welcome, consent, instructions, tasks, questionnaires, debriefing), with the number of trials per condition and an estimated duration for each phase; the durations sum to the session estimate.
  - Every Materials item appears at the point in the session where it is used.
  - The section says how every participant hears the same instructions and how cues that could differ between conditions are held constant.
  - The section says what happens if you get sick or the equipment breaks down.

### 11. Write the Planned Analysis section

- The **primary measure** is the one dependent variable your central conclusion rests on.
- Plan to look before you test: check for impossible values, missing data, and failed sessions; plot each dependent variable's distribution; and compute descriptive statistics. Time measures are often skewed (lopsided, with a long tail of slow responses), so look at the median as well as the mean.
- The right test depends on the design, each dependent variable's measurement scale (step 7), and its distribution; the non-parametric option fits data that are clearly not normal (bell-shaped) or are ordinal ([when you pick the test for each hypothesis, use the test table](#background-choosing-a-statistical-test)).
- The significance level is conventionally .05. A p value is how likely a difference at least as large as the observed one would be if there were no real difference; an effect size measures how large the difference is.
- *Running example:* the primary measure is movement time, reduced to one mean and one median per participant per distance-and-size combination. The devices are compared on each participant's overall mean with a t-test for independent groups, or Mann-Whitney U if the data are clearly not normal. Error rate, each participant's proportion of missed clicks, is compared the same way and reported alongside movement time. A line chart of movement time against target size (one line per device, with standard-error bars showing how precisely each mean is estimated) shows whether H3's interaction appears, and a mixed ANOVA, with a sphericity check for distance and size, tests it. With 12 per device, the study may be underpowered: a real but small difference could go undetected (a Type II error), so the results will lead with descriptive statistics and charts.
- **Done when:**
  - The primary measure is named.
  - The section says how trial-level data are reduced to the values tested.
  - The checks before testing are listed, including the median of each time measure.
  - Each hypothesis and research question from step 6 has a named test that matches the design, measurement scale, and distribution, with its non-parametric alternative where the test table lists one (otherwise how you will handle data that are clearly not normal) and the rule for choosing between them; any ANOVA with a within-subjects factor of three or more levels names its sphericity check.
  - Each exclusion criterion is listed with its defense and, like a failed session or an ineligible participant, is independent of how the participant responded to particular conditions; the plan reports every exclusion.
  - The significance level is stated, and the plan reports every p value, whether or not it supports your hypotheses, with an effect size.
  - All of the above is pre-specified.

### 12. Assemble the Appendix

- Start the consent form from a template; most review boards provide one. Repeating the disclosures below in the verbatim script lets participants hear what the consent form asks them to read. The disclosures include the consent elements of the American Psychological Association (APA) Ethics Code:
  - who you are, your affiliation, and, if you are a student, who supervises the study;
  - why the study is being run, for example for a course or a thesis;
  - its purpose, expected duration, and procedures;
  - the right to decline and to withdraw after starting, and the consequences of either;
  - foreseeable risks or discomfort, benefits, and incentives;
  - limits of confidentiality, who will see the data and results, and how long the raw data are kept (the step 1 data plan);
  - a named contact, with contact information, for questions about the research, and one for questions about participants' rights (often the review board's office).
- Write briefly, in plain language.
- Decide how to record consent. Participants typically sign, but a signature identifies them, so if a signed form would be the only record linking a person to the study and confidentiality is the main risk, ask whether your review board allows oral consent.
- *Running example:* a flyer seeking right-handed adults aged 18 to 22; a consent form covering every disclosure above; the session script with the debriefing; and a demographic questionnaire asking only age and handedness.
- **Done when:**
  - The Appendix holds every recruiting material, such as flyers; the informed consent form; the verbatim script; every questionnaire named in the Materials section; and the ethics-review documentation: an approval letter, a completed review form, or a statement that the study falls under an existing approval.
  - The section that uses each item refers to it.
  - The consent form and the script cover every disclosure above, and the stated duration matches the session estimate.
  - The consent form says how consent is recorded.
  - The script includes a point where participants can ask questions.
  - Every demographic question serves a need stated in the Participants section (data minimization) and has space for its answer.

### 13. Review the proposal and prepare to defend it

- Before you run the study, expect to present the proposal and answer questions about it from a supervisor, an instructor, a committee, or reviewers.
- Readers judge a proposal, like a paper, on seven questions: importance (does the problem matter?), credibility (will the methods support the conclusions?), ethics (could the work cause harm?), novelty (what is new?), external validity (will the results generalize beyond your sample and setting?), assumptions (are they realistic?), and readability (is it clear and well organized?).
- **Done when:**
  - You have reviewed the proposal against the seven questions above and revised it where it fell short.
  - You have presented the experiment at least once to a critical listener, such as a labmate, a classmate, or a colleague.
  - Each piece of feedback, and each question you could not answer, is recorded with what you did about it, and every revision is in the draft.
  - You can give the reason for every choice in the Design section.
  - The **Done when** of every step from 1 to 12 holds for the draft you will submit, since later steps revise earlier sections; the draft uses the required template, describes the full experiment rather than the pilot, follows the step 3 conventions throughout, and is within the length limit.

## Background Knowledge

Short refreshers on concepts the steps rely on.

### Background: variables and confounds

- Independent — manipulated by the researcher, with two or more levels.
- Dependent — a measure of participants' behavior.
- Control — a circumstance held constant, such as requiring right-handed participants.
- Random — a circumstance varied by chance, such as condition order or time of day.
- Confound — a circumstance that changes systematically with the independent variable, such as always serving one cola in a glass marked M and the other in a glass marked Q, so tasters may be choosing the letter rather than the cola.
- Random procedures — distinct from a random variable: random assignment (step 7) decides which condition each participant gets; random order decides the sequence of within-subjects conditions; random selection (step 8) draws the sample from a population and is the only one that supports generalizing to it.

### Background: design types and counterbalancing

- Between subjects — each participant gets one level. It needs more participants and random assignment, but it avoids carry-over and keeps sessions short.
- Within subjects — each participant gets several levels. It needs fewer participants and removes most individual differences, but carry-over means order must be counterbalanced or randomized.
- Factorial design — every level of each independent variable is paired with every level of the others.
- Mixed design — a factorial design with at least one between-subjects and one within-subjects factor.
- Counterbalancing — with conditions A and B, half the participants do A then B and half do B then A. It assumes symmetric carry-over (step 7).
- Latin square — with many conditions, choose orders so each condition appears in every position equally often; in a balanced square each also precedes and follows every other equally often. For four conditions: ABDC, BCAD, CDBA, DACB.

### Background: choosing a statistical test

Find the row for your design and the column for the dependent variable's data. Categorical outcomes include task success or failure and the option a participant chose.

| Design                                                                                   | Interval or ratio, roughly normal                           | Ordinal, or clearly not normal                  | Categorical                                                        |
| ---------------------------------------------------------------------------------------- | ----------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------ |
| Two independent groups                                                                   | t-test for independent groups                               | Mann-Whitney U                                  | Chi-square test or Fisher's exact test                             |
| Two conditions with the same or matched participants                                     | t-test for related samples                                  | Wilcoxon matched-pairs signed-ranks             | McNemar test                                                       |
| Two or more independent groups, one independent variable                                 | One-way between-subjects ANOVA                              | Kruskal-Wallis                                  | Chi-square test                                                    |
| Three or more conditions with the same or matched participants, one independent variable | Within-subjects (repeated-measures) ANOVA; check sphericity | Friedman                                        | Repeated-measures logistic regression (two categories)             |
| Factorial                                                                                | Factorial ANOVA, or mixed ANOVA for a mixed design          | Ordered logistic regression (ordinal data only) | Factorial logistic regression (two categories, independent groups) |

These are common choices; other valid tests exist. Sphericity is the assumption that the variances of the differences between every pair of conditions are equal; statistics software reports a check, so look for it.
