# Report template

Keep the headings, their order, and their numbering; `scripts/check_report.py` looks for them. The bullets are questions; answer them in prose. Replace every `{{placeholder}}`. "Background: ..." names a section of `background.md`.

______________________________________________________________________

# Critical analysis: {{paper title}}

{{Authors (year). Title. Venue, pages or DOI.}} Version read: {{preprint and number, or published}}. Report written {{date}}.

## 1. Context

### 1.1 Title and authors

- Title: short and to the point? Tells you what to expect?
- Authors: known to you? How many? What does the order say?
- Affiliations: one institution or many? Which departments? Well known? The authors may be students.
- Their field?

### 1.2 Publication venue

- Conference, journal, workshop, technical report, or preprint (Background: types of sources, and how current they are)? What does that imply about review rigor?

### 1.3 The authors' previous work

- What have they done before in this area?

### 1.4 Motivation

- Why is the problem important? Does the paper motivate the research, state the contribution, and preview the rest?

### 1.5 Related work and references

- What similar research exists?
- Does the paper cover related work and background, discuss the relevant research, and establish the gap it fills?
- Is the related work comprehensive? Is it biased? Two checks (Background: types of sources, and how current they are):
  - Tree backward: follow the reference list to the works the paper builds on. Are they the field's recognized foundations, or idiosyncratic picks?
  - Tree forward: take one key cited reference and check, in a citation index, whether recent work citing it is conspicuously absent here. Journal publication lags a few years, so missing only the very latest work is not necessarily a gap.
- The references, counted: enough? What kinds (Background: types of sources, and how current they are)? How many include an author? How many from the authors' institution? Any you recognize? Span of years?

## 2. Summary

The abstract's content (problem and its significance, method, results, conclusion) at greater length.

### 2.1 Problem

- The research questions, hypotheses, objectives, or goals.
- What did the authors set out to do? What problem does the paper explain?

### 2.2 Method

- What did the authors do?
- Which method family: experiment, correlational observation, survey, archival research, or qualitative design (Background: the research-method menu)? What can the results therefore show, and not show?
- For an experiment, report as the paper should have:
  - Participants: how selected; characteristics (age, gender, education, etc.).
  - Materials: hardware and software.
  - Procedure: location; how the study proceeded.
  - Design: independent and dependent variables, how defined and measured; design type (Background: designing an experiment); if within-subjects, how order effects were handled.
  - Pilot study run? Participant count versus similar published experiments?
- For a qualitative study: how were participants or sites purposefully selected? What data? What coding and analysis, and did it yield themes, categories, aggregate dimensions, or a grounded model?
- Otherwise: what methods, techniques, or process?

### 2.3 Results

- Big picture first, then details.
- How was the data analyzed (here, or at the end of 2.2)?
- For an experiment: descriptive statistics first, tables for numbers, charts with honest axes for the most interesting results, then inferential statistics, also in tables (Background: interpreting quantitative results). Interpretation belongs in 2.4.
- For a qualitative study: validated as Background: qualitative methods describes? Description rich enough to carry the themes or model?
- Otherwise: what did the process, methods, or techniques produce?

### 2.4 Discussion

- Implications? The authors' interpretation? How has the work advanced the field?
- Why do the authors think they got these results? Practical value?
- Limitations?
- Future research the authors discuss, plan, or leave open? What else should be explored?

### 2.5 Conclusion

- Does it summarize methods, results, and discussion, and restate the significance?
- Acknowledgements for non-author helpers and funding?

## 3. Critical discussion

Cover all nine topics, in any order. Give each what you found, the locator, and your judgment.

### Importance

- Is the problem important? How significant is the contribution? The big ideas?

### Credibility

- Do you trust the methods? How likely are the conclusions to be correct?
- Affiliation earns no trust. Venue rigor (Background: types of sources, and how current they are) weighs in but excuses no check below.
- For a correlational study: causality implied where not established (Background: the research-method menu)?
- Which threats to internal validity apply (Background: designing an experiment)? Demand characteristics controlled? Questionable research practices visible (both in Background: treating participants fairly, and research integrity)?
- For a qualitative study: findings validated as Background: qualitative methods describes?
- Close with your confidence that the conclusions are correct, high, medium, or low, and the evidence that would raise it.

### Novelty

- Novel approaches? Obvious, or clever? New information? Incremental, or a real departure?

### Applicability

- Practical applications?
- Can the reader apply it to their own projects? If the reader is unknown, say who could use it and for what.
- Could other researchers or practitioners apply it?

### Generalizability

- Do the results hold only in the paper's situation, or more widely?
- Did tight control buy internal validity at the cost of external validity (Background: designing an experiment)?
- For a qualitative study: how were participants or sites selected (Background: qualitative methods), and how far do the authors claim the themes or model extend?

### Scalability

- Does it scale? Still relevant at a larger or smaller scale?

### Assumptions

- What do the authors assume, and is it realistic?
- For a parametric test: assumption checked (Background: interpreting quantitative results)?
- For within-subjects counterbalancing: leans on symmetrical transfer (Background: designing an experiment), and is that reasonable here?
- How are the key variables defined, especially vague ones? Do you agree?

### Readability

- How hard to understand? Sentences and paragraphs well written? Structure logical, flow smooth? Culturally neutral? Vocabulary needlessly obscure?

### Ethics

- Is the work a good idea? Could it lead to harm, and are the authors aware of that?
- IRB approval and informed consent reported, with how consent was obtained and how confidentiality and privacy were protected (Background: treating participants fairly, and research integrity)?
- If deception: justified as necessary? Debriefed? Blatant misleading, or withholding?
- With human subjects: signs of fair treatment?
- Signs of research misconduct? Report them as observations; an allegation is never yours to make.

## 4. Coverage

- Not read: parts of the paper or supplements, and why.
- Not checked: checks you could not run, each with its reason.
- For the reader to double-check: claims resting on inference or an unconfirmed source.
- Verification: fresh-context pass or self-verified; claims checked; claims changed.
