# Reader-reaction methods for Report review

**Verdict (updated 2026-08-26).** Add no new review stage or gate. Inside the ordinary review of a frozen working Report, run one bounded **reader-use pass**: define one intended reader and one realistic decision, collect a location-specific plus/minus trace on the first read, then ask the reader to restate the Report's answer, make the decision, name the passages that drove it, and identify the remaining blocker. A response from an actual target reader is reader evidence. The same protocol run by an LLM—including Grammarly Reader Reactions—is only a **proxy hypothesis**; it must never be presented as what the audience thinks. Citation verification and claim fact-checking keep their existing scopes.

This recommendation transfers methods developed for public-information and technical documents to analytical Reports. The transfer is an inference, not a directly validated result: the source studies did not test this repository's Report form.

## What the established methods establish

### Reader feedback answers a different question from expert review

Schriver distinguishes text-focused, expert-judgment, and reader-focused evaluation by how directly each captures the intended audience's interaction with a document. Reader-focused methods can be concurrent, observing comprehension and use as they happen, or retrospective, eliciting responses after the read ([Schriver 1989](https://doi.org/10.1109/47.44536)).

That distinction has empirical bite, though the available study is narrow. When Lentz and de Jong asked technical writers and subject/audience experts to predict problems that readers had found in one government brochure, the experts predicted less than 15% on average, raised many different problems, and agreed little with each other ([Lentz and de Jong 1997](https://doi.org/10.1109/47.649557)). Expert review therefore cannot be relabeled reader reaction. The two instruments may find different problems and should complement each other.

### Plus/minus marking supplies a low-interruption core

The **plus-minus method** asks a participant to read from start to finish, marking positive and negative reading experiences beside any text element; a retrospective interview then elicits the reason for every mark. Marks may concern comprehension, relevance, appreciation, or another reaction, so the method produces both a locator and an explanation without directing the reader toward a preset defect class ([de Jong and Schellens 1998](https://doi.org/10.1109/IPCC.1998.722086)).

In the authors' validation series, six public-information brochures were revised from plus/minus feedback. Target readers preferred the revised fragments in all six motivated-choice experiments; five of six independent-group experiments improved at least one measured outcome such as comprehension, persuasion, or perceived user-friendliness, although several individual outcomes remained nonsignificant. The method also exposed two limits important here: self-report can miss unrecognized comprehension problems or invite pleasing-the-facilitator responses, and the frequency of a reported problem did not track expert-rated importance (mean correlation `r = .08`) ([de Jong and Schellens 1998](https://doi.org/10.1109/IPCC.1998.722086)). A reaction is a diagnostic observation, not a vote or an automatic edit.

### Gist-back and a decision task make the reaction useful

The Centers for Medicare & Medicaid Services' document-testing guide combines four methods in a feedback session: think aloud, questions, realistic tasks, and behavioral observation. It recommends asking readers to explain the material in their own words and, for usability, asking them to use the material to make a decision; the task shows whether they can use the document unassisted for its intended purpose ([CMS Toolkit Part 6, chapter 1](https://www.cms.gov/Outreach-and-Education/Outreach/WrittenMaterialsToolkit/Downloads/ToolkitPart06Chapter01.pdf)). Its method-selection chapter says these methods normally work in combination, not as independent phases, and identifies task performance as the strongest direct test of intended use ([CMS Toolkit Part 6, chapter 7](https://www.cms.gov/Outreach-and-Education/Outreach/WrittenMaterialsToolkit/Downloads/ToolkitPart06Chapter07.pdf)). This is practitioner guidance rather than a controlled Report experiment, but it directly supplies the missing decision probe.

### Preserve the first reaction before asking for reasons

A meta-analysis of 94 verbal-reporting studies with nearly 3,500 participants found that simple concurrent thinking aloud did not measurably change accuracy (`r = -0.03`), but directed explanation improved performance relative to silent controls, and verbal-report procedures tended to lengthen task time ([Fox, Ericsson, and Best 2011](https://doi.org/10.1037/a0021663)). The practical consequence is ordering: collect undirected marks or immediate thoughts first; ask for explanations, diagnosis, and decision reasoning afterward. Full concurrent think-aloud remains an optional observation method when navigation or attention matters, not the default solo instrument.

### An LLM can walk the scenario, but it cannot supply audience evidence

LLM persona evidence is task-specific and conflicting. Argyle and colleagues reproduced several aggregate patterns in US survey responses by conditioning GPT-3 on thousands of real respondents' detailed backstories, but they explicitly did not test individual-level correspondence ([Argyle et al. 2023](https://doi.org/10.1017/pan.2023.2)). On a different benchmark, language-model opinions remained substantially misaligned with 60 US demographic groups even after explicit group steering ([Santurkar et al. 2023](https://proceedings.mlr.press/v202/santurkar23a.html)). A separate experiment spanning 162 role prompts, four model families, and 2,410 factual questions found no general performance gain from adding personas and found persona effects difficult to select predictably ([Zheng et al. 2024](https://aclanthology.org/2024.findings-emnlp.888/)).

For a solo workflow, give the model a concrete use scenario, relevant prior knowledge, and stakes—not a demographic costume—and label its output `proxy hypothesis`. It can cheaply expose a plausible misreading or missing decision input. Only a real intended reader can establish that an audience member actually reacted that way.

## Grammarly productizes the proxy, not reader evidence

Grammarly Reader Reactions packages an LLM reader simulation into a writing interface. Its user guide says the agent infers or accepts a target audience, scans the full document, and predicts key takeaways, open questions, potential confusion, likely resonance, and what that audience may remember. Inline bars lead to suggested actions and example rewrites ([Grammarly Reader Reactions user guide](https://support.grammarly.com/hc/en-us/articles/38552519578893-Reader-Reactions-user-guide)). The product page adds preselected or custom reader profiles, while the Superhuman Go guide also names tonal mismatches among the outputs ([Grammarly product page](https://www.grammarly.com/ai-agents/reader-reactions), [Superhuman Go agent guide](https://help.superhuman.com/hc/en-us/articles/46242137727757-About-Superhuman-Go-agents-and-connectors)).

That interface adds convenience and useful output categories, but it does not observe a reader:

| Dimension        | Grammarly Reader Reactions                               | Proposed reader-use pass                                      | Consequence                                                                  |
| ---------------- | -------------------------------------------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Audience         | Inferred, selected, or custom profile                    | Explicit role, relevant prior knowledge, decision, and stakes | Keep the explicit use card; hidden audience inference can test the wrong use |
| Initial response | Model scans the document                                 | Undirected human `+`/`-` trace, or a labeled LLM emulation    | Generated locators are hypotheses, not an observed first-read trace          |
| Synthesis        | Likely takeaways, memory, questions, confusion, and tone | Gist, decision, warrant, blocker, then explanations           | Takeaways and questions map well; Grammarly omits the decision-use test      |
| Revision         | Suggested actions and insertable example text            | Reviewer diagnoses only after the frozen pass                 | Preserve the reaction before accepting or generating revisions               |
| Evidence class   | AI prediction                                            | Human observation or explicitly labeled LLM proxy             | Never count Grammarly outputs as real-user evidence or audience prevalence   |

Grammarly's own audience-writing guide draws the same evidence boundary: it calls peer or real-reader feedback the most valuable input, recommends a human read when possible, and positions Reader Reactions afterward as a preview ([Grammarly audience guide](https://www.grammarly.com/blog/writing-tips/know-your-audience/)).

The official product page, support guide, launch announcement, and Go guide reviewed on 2026-08-26 provide no validation method, benchmark, calibration result, or comparison between predictions and actual target-reader responses ([Grammarly launch announcement](https://www.grammarly.com/blog/company/grammarly-launches-ai-agents/)). The product page offers two named testimonials, which support perceived writer usefulness only, and the current non-enterprise terms disclaim the factual accuracy and use-case suitability of generative-AI outputs ([Grammarly Terms of Service](https://www.grammarly.com/terms)). A separate CHI study of a similar GPT-3.5 persona-feedback prototype—not a study cited by Grammarly and not a test of Reader Reactions—found that 16 writers valued the perspectives and revised their work, but also found feedback verbose and unspecific and emphasized limited representativity. It evaluated the writer experience, not agreement with target readers ([Benharrak et al. 2024](https://doi.org/10.1145/3613904.3642406)). This is evidence for the ideation value of a proxy, not its audience accuracy.

### Data and governance change the adoption boundary

Running Reader Reactions sends document context across an external service boundary. Grammarly says the agent scans the full document; its product FAQ says working-environment data used by agents is stored temporarily. That narrow statement does not make a Docs document ephemeral: Grammarly's privacy FAQ says documents created in its editor remain stored until the user deletes them. The same FAQ says generative-AI prompt type, prompt text, and context go to vetted service providers and that those providers may not train their models on user content ([Reader Reactions product FAQ](https://www.grammarly.com/ai-agents/reader-reactions), [Grammarly privacy and security FAQ](https://support.grammarly.com/hc/en-us/articles/20916119474829-Privacy-and-security-FAQs)). The current platform privacy policy also covers Grammarly and Docs, treats drafts, screen content, documents, and files as user content, and sets retention by purpose and account configuration ([Superhuman privacy policy, effective July 6, 2026](https://superhuman.com/legal/privacy-policy)).

Training controls depend on the account. Product Improvement and Training is on by default for individual Free, Premium, and single-user Pro accounts and for multi-user accounts bought directly from the website; users or administrators can opt out. It is off by default for Education and sales-purchased Business, Pro, and Enterprise accounts. Even with content training off, Grammarly may still use non-content, aggregated, or de-identified writing statistics for improvement ([Grammarly Product Improvement and Training Control](https://support.grammarly.com/hc/en-us/articles/25555503115277-Product-Improvement-and-Training-Control)). Organizational administrators can disable Reader Reactions, although agents are on by default when Docs is enabled ([Grammarly agent-access controls](https://support.grammarly.com/hc/en-us/articles/40781455235725-Control-which-AI-agents-your-team-can-use)).

Therefore, do not make Grammarly a default dependency or upload a Report merely because the feature is available. A sanctioned trial should use a non-sensitive or redacted Report, verify the governing contract and training setting, minimize supplied context, delete the stored document afterward, and record the product and access date with `mode: LLM proxy hypothesis`. Confidential, personal, licensed, or otherwise restricted material requires separate authorization. Borrow the audience-profile, takeaway, open-question, tone, and inline-locator ideas where useful; the existing `reader_and_decision`, `gist`, `blocker`, and `trace` fields already cover them.

## Recommended one-pass instrument

Default budget: one reader/use card, one uninterrupted read, and one retrospective probe. Do not create a panel, score, or second sign-off.

### 1. Freeze the use case

Before showing the Report, record:

- **Reader:** the intended role and only the prior knowledge relevant to use.
- **Decision:** one concrete choice or action the Report is meant to support.
- **Stakes and constraints:** what matters to that choice, including time or risk.
- **Mode:** `target-reader evidence` or `LLM proxy hypothesis`.

The Report stays unchanged during the pass. Do not provide the intended conclusion as part of the role card; that would cue the answer being tested.

### 2. Capture the first-read trace

Ask the reader or proxy to read once without editing, fact-checking, or proposing fixes:

- Mark `+` beside a passage that makes the answer or decision clearer, more credible, or easier to use.
- Mark `-` beside a passage that confuses, weakens trust, obscures a consequence, or blocks the decision.
- For each mark, preserve the heading or exact short excerpt and the immediate reaction. Do not explain the reaction yet.

Positive marks matter: they identify load-bearing material that a revision should preserve. If factual doubt affects the reaction, record the doubt as a blocker at its locator rather than investigating it mid-read.

### 3. Run the retrospective decision probe

After the last page, ask exactly these questions:

1. In your own words, what answer or recommendation does this Report give?
2. Given the stated decision, what would you do now?
3. Which Report passage most influenced that choice, and why?
4. What material uncertainty, missing alternative, or ambiguity would stop you from acting?
5. Now explain each `+` and `-` mark.

Record the result in a small, fixed shape:

```yaml
mode: target-reader evidence | LLM proxy hypothesis
proxy_system: ... # omit for a target reader; otherwise record product/model and date
reader_and_decision: ...
gist: ...
decision: ...
warrant: ...
blocker: ...
trace:
  - locator: ...
    mark: + | -
    reaction: ...
    decision_consequence: ...
```

### 4. Triage inside the existing review

The reviewer, not the reader, diagnoses each consequential mismatch:

| Observed issue                                                     | Existing owner                                                           |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| The gist, relevance, organization, tone, or decision path misfires | Revise in the normal Report review                                       |
| A citation, identifier, or quotation may be wrong                  | Route to [`verify-citations`](../../../skills/verify-citations/SKILL.md) |
| A claim may overstate or misread its cited source                  | Route to [`factcheck-draft`](../../../skills/factcheck-draft/SKILL.md)   |
| The decision requires domain judgment or a real audience reaction  | Escalate to the person or recruit one target reader                      |

Prioritize a finding when the restated gist differs from the intended answer, the decision changes for an unintended reason, or the central warrant is absent or misunderstood. Do not prioritize by number of marks, repeated model samples, or persona votes. One pass can discover a problem; it cannot estimate prevalence.

## Boundary and adoption decision

Source verification asks whether citations and quoted evidence resolve and match. Fact-checking asks whether the Report's claims fairly follow from their sources. Reader reaction asks what an intended user understands and does with the assembled Report. None answers either of the other two questions, so a reader-use pass neither clears nor reopens their results.

Adopt the instrument as an optional lens within ordinary Report review, with a vendor-independent LLM proxy as the zero-recruitment default and one real target reader for consequential or audience-sensitive decisions. Grammarly Reader Reactions may implement that proxy only when its data boundary is acceptable; it adds no new evidence class and does not replace the decision probe. Report the mode and tool honestly, retain location-specific observations, keep model-suggested edits out of the frozen pass, and stop after the single probe. Revisit only if repeated use shows that the pass changes no revisions, or if a real-reader pilot supplies enough observations to justify a different question set.
