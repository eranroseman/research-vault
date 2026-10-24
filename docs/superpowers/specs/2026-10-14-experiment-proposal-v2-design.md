# Design: experiment-proposal v2, the plugin judged by the proposal it produces

Disposition: superseded-by: 2026-10-23-experiment-proposal-v3-design.md (2026-10-24; every decision v3 does not name stands)

Date: 2026-10-14. Status: approved in brainstorming, awaiting spec review. Branch: `experiment-proposal-v2`. Supersedes `docs/superpowers/specs/2026-10-13-experiment-proposal-plugin-design.md` (the first spec), whose decisions stand except where this spec changes them.

## Goal

The plugin exists to produce one document: the course's experiment proposal. Everything in it is judged by whether it contributes directly to that document. The assignment, which this spec calls **the lens**, asks for a proposal of 2,000 to 4,000 words excluding references and appendices, in the CHI 2025 publication format, with these sections in this order: Introduction (a quick overview; the motivation, the problem and its significance; a bullet list of contributions, what a reader gets from the final report), Literature review (work that motivates the problem, justifies the approach and resembles the study; 15 to 20 references, found by following citations), Research questions or Hypotheses, Participants (how participants are recruited and selected for the experiment to be conducted after the pilot study; recruiting materials in the appendix), Materials (the software and hardware participants interact with), Procedure (where and how the experiment is conducted; the script in the appendix), Design (independent variables marked within or between subjects, dependent, control and random variables, each defined precisely, and how the dependent variables are measured), and an Appendix holding the recruiting materials, the script or protocol, the informed consent form with the federal consent elements and a statement that the study is under the instructor's supervision, and every questionnaire.

Version 0.1.0 of the plugin was built from the guide's thirteen steps and evaluated on 2026-10-14 against a real study idea. Two of its parts serve nothing the lens asks for, and they were its most expensive and most defect-prone: the Planned Analysis machinery (mixed-model items, the test-selection deviations) serves a section the proposal does not have, and the power simulation (an R template, a parameter batch, four R runs of about an hour, a BLOCKED and waived state machine) serves one sentence that the guide lets a reason from similar experiments satisfy. The guide's own rule applies: the template's section list overrides the typical sections. Both parts leave.

What the lens asks for and 0.1.0 did not carry, it gains: the section list and order, the word bounds, the reference count, the contributions list and the supervision sentence become checks a script can run.

The second lesson of the build was that every defect the reviews found lived in prose, and prose can only be reviewed. Where a shape can be checked by code, it is: a checker script owns the shapes of the brief and the review, and the skills are rewritten under the writing-for-agents reference so that each file carries ordered steps with completion criteria, and the shapes they produce sit in disclosed reference files that the checker also reads.

## What stands from the first spec

Unchanged and not restated here: the packaging (`plugins/experiment-proposal/`, the marketplace entry, the install id); four skills invoked by name only, each with `disable-model-invocation: true` and a Codex `agents/openai.yaml` with `allow_implicit_invocation: false`; the vendored sources, their pins, provenance headers and licence files; the HCI researcher as a vendored subagent; `lit-search` as our `SKILL.md` over the nine vendored scripts; `the-ethics-board` as a vendored skill; research-grill as a separate install with no declared dependency; the guide as documentation the skills never read; the artifacts `proposal/design-brief.md` and `proposal/review.md`; the freeze by commit and the amendment rule; the Codex relative-path fallback; the git discipline. The sourcing verdicts stand for every component that stays; the rows for simr, statistical-power and the power template are retired by this spec (see Bookkeeping).

## Decisions

| Question                   | Decision                                                                                                                                                                                                                                           |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The lens                   | The course assignment's requirements, as the Goal states them. Anything that does not directly contribute to that proposal is dropped.                                                                                                             |
| Planned Analysis           | Dropped: the checklist loses step 11 and the analysis clauses elsewhere; the mixed-model default and the test-table deviations are retired.                                                                                                        |
| Power analysis             | Dropped: no R template, no prerequisite check, no parameter batch, no BLOCKED or waived states. The participant count is justified by similar experiments and a stated reason, as the guide's step 8 allows.                                       |
| Equivalence (TOST) power   | Out, with the rest of power; issue #222 closes as superseded.                                                                                                                                                                                      |
| The checker                | Build: `plugins/experiment-proposal/scripts/check_proposal.py`, standard library only, with `brief`, `review` and `draft` subcommands. Glue tier: one line of reason, the shapes it checks were where every review finding landed.                 |
| Skill texts                | Restructured and pruned under the writing-for-agents reference: steps with completion criteria in each `SKILL.md`; the shapes in disclosed reference files; leading words; positive phrasing; word budgets held by tests.                          |
| The subagent's tools       | A marked local edit to the vendored frontmatter: `tools: Read, Grep, Glob`. It answers from its knowledge and the material and runs nothing.                                                                                                       |
| The version                | One writer, `plugin.json`; the brief's `Checklist:` line is read from it at run time; the README points at it. This release is 0.2.0, tagged `experiment-proposal--v0.2.0`.                                                                        |
| The assignment's mechanics | Carried as parameters confirmed at item 3.1 with this course's values as defaults: the section list and order, 2,000 to 4,000 body words, 15 to 20 references, the supervising instructor's name. `review` runs the draft checker with them first. |
| Substance tests            | Kept (items 13.6 to 13.11): they improve the proposal and cost only review time.                                                                                                                                                                   |
| The defend hand-off        | Kept as one closing paragraph of `review`; research-grill is detected by reading the installed-plugins file, as 0.1.0 learned.                                                                                                                     |
| Evaluation                 | Scenarios 2, 3, 5 and 6 re-run three times each at 0.2.0 with revised bars; scenario 4 (no R) deleted; baseline not re-run; one real-material amendment session on the author's own project, recorded, no bar.                                     |

## The checklist under the lens

`references/checklist.md` keeps its grammar, IDs and the dependency graph for the items that remain. The provenance note names the lens as a second source beside the guide.

Removed: every step 11 item (11.1 to 11.11); items 6.6 and 6.7 (the smallest effect size of interest and the decision rule, both analysis additions); items 8.6 and 8.7 (the effect-size ranking and the sensitivity range). Their credits to statistical-power leave with them.

Changed:

- 2.1 loses its analysis clause: every Method value is decided or marked as one the pilot will settle: each independent variable with its levels and its within- or between-subjects label, each dependent variable with its unit, the number of participants, the materials, and the session phases.
- 3.1 reads: the template's requirements are identified and recorded (its section list and order, its word bounds and whether references and appendices count, its reference bounds, its citation style, and the supervising instructor's name), the course's values being the defaults when the template leaves one unsaid; it stays attested.
- 3.2 reads: the draft has a heading for every section the template lists, in the template's order, with Design separate from Procedure (the guide's "Planned Analysis may instead close the Method" clause goes).
- 4.2 reads: the section states the motivation (why this project), the problem, and its significance with citations.
- 4.3 reads: the section lists the contributions as bullets, each saying what a reader will get from the final report.
- 5.1 gains the count: the review cites work that motivates the problem, work that justifies the approach, and similar studies, and the reference list holds the number of references the template asks for.
- A new 6.6 is the guide's own outcomes item: each hypothesis's possible outcomes, including a non-significant one, are listed and each is interpretable. It depends on 6.2 and is review-only. The ID is reused: a 0.1.0 brief's entry 6.6 is the old effect-size item, and an amendment naming 6.6 means the new one.
- 8.5 reads: the number is justified by similar experiments and a stated reason for the count, says how the pilot will refine it, and is pre-specified. It depends on 7.3 and 7.6 and stays in the design tree.
- 12.3 adds: the consent form states that the study is under the supervision of the named instructor.
- 13.5 reads: the draft to be submitted satisfies every item of steps 1 to 12, uses the required template with its section list in order, describes the full experiment rather than the pilot, follows the step 3 conventions (item 3.3) throughout, and is within the word bounds excluding references and appendices.
- 13.11's executability test asks that the proposal states how each dependent variable is measured, in place of "states a concrete analysis".
- The deviations section records: step 11 is not checked, because the lens's section list has no Planned Analysis section and the guide's rule that the template overrides its typical sections applies; the power analysis is not run by the plugin.

A dependency on a removed item is re-pointed to the nearest surviving item the removed one stood on (2.1 and 13.10 lose 11.4 and stand on 7.6; 8.5 stands on 7.3 and 7.6; the new 6.6 on 6.2). The count is 67 items. The design tree is 21 items: 1.1 to 1.3, 2.2 to 2.5, 6.1, 6.2, 6.5, 7.1 to 7.9, 8.3 and 8.5. The attested items are 3.1, 5.2, 13.1 and 13.4; the defend-stage items are 13.2 and 13.3. The dependency graph stays acyclic; a test proves it.

Item 3.1 carries the assignment's mechanics: when the user confirms the template, `review` records the section list and order, the word bounds, the reference bounds and the supervisor's name, with this course's values offered as the defaults.

## The checker

`plugins/experiment-proposal/scripts/check_proposal.py` is our own code, standard library only, Python 3.11 or later, with no network and no writes. It is the single source of truth for the shapes of the brief and the review; the reference files describe the same shapes in prose and name the checker. Exit 0 means clean; exit 1 prints one defect per line as `<file>:<line>: <message>`; exit 2 means a file it could not read. It reads the checklist from the plugin folder it lives in, so the item set is never duplicated.

`check_proposal.py brief proposal/design-brief.md` checks: the three header lines (`Draft:` with a path, `Status: open` or `Status: frozen <YYYY-MM-DD>`, `Checklist: experiment-proposal <semver>`); the sections `## Decisions`, `## Looked up`, `## Open items` and an optional `## Amendments`, in that order; one `### <ID> <title>` entry per design-tree item that is settled, pilot-settles or provisional (a provisional entry's Decision is the recommendation, so the user sees it in place), the ID in the checklist's design tree; exactly the five lines `- Decision:`, `- Rationale:`, `- Would change if:`, `- Status:` and `- Source:` per entry, in that order; a Status of `settled`, `pilot settles` or `provisional`; every provisional entry also listed under Open items, and every Open items line naming an item matching an entry; a Decision line of at most 400 characters; a frozen brief holding an entry for every design-tree item; Open items as provisional items first, then commands; amendment headings of the shape `### <YYYY-MM-DD>, item <ID>, <title>` with the lines `- New decision:`, `- Reason:` and `- Replaces:`. A brief whose `Checklist:` version is older than the checker's shape version, 0.2, is checked on its header and Amendments only, with one stderr note saying so; its frozen entries are never edited.

`check_proposal.py review proposal/review.md` checks: the header lines (`Brief:`, `Draft:`, `Date:`, `Checklist:`); `## Items` with one row per item of steps 1 to 13 (13.2 and 13.3 reading `not checked`), each `- **<ID>** <result>` with the result `pass`, `pass narrowly`, `fail`, `fail (waived)` or `not checked`, in checklist order; a quoted passage with a location on every draft-checked pass; `confirmed by the user, <date>` on every attested pass; `fix N` numbers contiguous from 1 in order of appearance across the whole file; `## Cross-section consistency`, `## Brief against draft`, `## Substance tests`, `## Summary`, `## Waivers` and `## Hand-off` present, in that order; the Summary counts recomputed from the rows and the sections and compared; the Hand-off holding either the defend command or the two install commands.

`check_proposal.py draft proposal/draft.md [--sections "..."] [--words 2000-4000] [--references 15-20] [--supervisor "<name>"]` checks the assignment's mechanics with this course's values as defaults: the section headings present in the given order (matched case-insensitively on the heading text, so `## Literature Review` and `## Literature review` both count); the body word count, where the body is everything before the References heading and outside the Appendix, counted as whitespace-separated tokens; the number of entries in the reference list (list items or paragraphs under References); a bullet list under the Introduction heading; and a sentence in the Appendix's consent form containing "under the supervision of" followed by the supervisor's name. Each miss is one line naming the mechanic and the number found.

The checker does not judge the truth of a quote, the sense of a design, or the draft's prose. `design` runs `brief` before the freeze and refuses to freeze on a defect; `review` runs `draft` first and turns each miss into a failing row of the item that owns it (3.2 for sections, 13.5 for words, 5.1 for references, 4.3 for the bullet list, 12.3 for the supervision sentence), and runs `review` on its own file before it finishes, fixing its own defects before reporting. The plugin tests run all three over fixtures.

## The skills, restructured

The layout after this spec:

```text
plugins/experiment-proposal/
  references/
    checklist.md                 the 67 items
    brief.md                     the brief's shape in prose; names the checker
    review.md                    review.md's shape, the result words, the counting rules, the hand-off text; names the checker
  scripts/
    check_proposal.py            the checker
  skills/
    design/SKILL.md              steps only
    review/SKILL.md              steps only
    lit-search/SKILL.md          pruned in place
    the-ethics-board/            vendored, unchanged
  agents/
    hci-researcher.md            vendored; two marked frontmatter edits (name, description routing sentence) plus the tools line
```

`templates/` is deleted. The two shape files sit beside the checklist because two user-invoked skills cannot share reference through the skill system; they are plain files any skill points at.

Writing-for-agents, applied as rules the tests can hold:

- Each `SKILL.md` we own is an ordered list of steps, each ending on a completion criterion the checker or the user can verify; reference that only one branch reaches is disclosed behind a pointer that names the file and the branch ("when the extraction table is shown, follow `references/brief.md` for the shape"; the `${CLAUDE_PLUGIN_ROOT}` form first, the relative form after it for Codex).
- Target behaviour is stated where it applies; the `## Rules` lists of 0.1.0 go, and the few hard guardrails that remain are paired with the positive target.
- The leading words are `frozen`, `provisional`, `pilot settles`, `the frontier`, `the material`, `the draft`; each is used as a token and defined once, in the reference file that owns it.
- No cached environment facts: no version strings, no install lists beyond the one command a step runs; the README carries prerequisites.
- Word budgets, held by tests and moved only by a spec edit: `design/SKILL.md` at most 1,400 words; `review/SKILL.md` at most 1,100; `lit-search/SKILL.md` at most 650; `references/brief.md` at most 700; `references/review.md` at most 800.
- Frontmatter form unchanged: user-invoked, one human-facing description line each; the description lines are reworded.

`design`'s steps: check git; read the material the user names and the folder it points at, nothing else in the project; extract and show the table; run rounds over the frontier (the 21-item tree, the question format of 0.1.0 unchanged); consult the subagent on counterbalancing, validity threats and confounds; settle item 8.5 from the user's similar experiments and reason; write the brief in the shape `references/brief.md` gives; run the checker; freeze by commit with the user's approval; amend by appending. A bare "yes" records the recommendation's basis as the rationale.

`review`'s steps: read the brief (stop when missing or not frozen), the draft, the checklist; confirm item 3.1's mechanics with the user; run the draft checker; check every item (quote on every draft-checked pass), cross-section consistency, the brief against the draft, the six substance tests; write review.md in the shape `references/review.md` gives and run the checker on it; apply only the fixes the user picks, re-check what they touch and item 13.5, rewrite the closing sections; record waivers; end with the hand-off printed in full, every time.

`lit-search`: the index report before the first round (which indexes will answer; the OpenAlex key present or absent; a Semantic Scholar key is not used); the target the template states (15 to 20 references, each kept with the claim it supports); keyword rounds, snowballing, the stop rule on a barren snowball round; the seeds request when the user gave none.

## The subagent

`agents/hci-researcher.md` gains a third marked local edit in its frontmatter, `tools: Read, Grep, Glob`, with its comment line and a clause in the provenance header's rename note; THIRD-PARTY-NOTICES and ATTRIBUTION name all three edits. `design` delegates one question per call with the decisions so far and the material's relevant passages, for counterbalancing (item 7.5), validity threats and confounds (items 7.7 and 7.9), and wherever a recommendation needs HCI judgment. The install test's delegation check re-runs once to confirm the agent still loads and still stays unprompted-free.

## README, attribution, notices

The README loses the R prerequisite and the analysis defaults, gains the lens (what the plugin produces, the assignment's mechanics and their defaults, how to override them at item 3.1), a headless-use note (the allowed-tools list that works: `Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)`; compound shell commands are refused by the permission layer), and two vendored-skill facts: `the-ethics-board` writes `proposal/ethics-review.md` and its transcript's researcher answers are the simulation's; `lit-search` does not use a Semantic Scholar key. ATTRIBUTION loses the simr row and the statistical-power credit, keeps research-grill, and names the subagent's three marked edits; THIRD-PARTY-NOTICES likewise.

## Tests

`tests/test_experiment_proposal_plugin.py` keeps the manifest, frontmatter, Codex metadata, provenance header, notices, checklist grammar and graph, vendored-script and README tests, with the sets and counts updated (67 items, the 21-item tree, the attested and defend-stage sets, the `tools:` edit); the R template tests go. The substring assertions on the skill texts shrink to what the checker cannot carry: pointers resolve; every cited item exists; the status words in `references/brief.md`, `references/review.md` and the checker agree (the test reads all three); the attested set the review skill names equals the checklist's; the word budgets.

`tests/test_experiment_proposal_checker.py` (planned) runs the checker in a subprocess: the scenario 5 brief and a review.md built from the reference file's example pass; a draft fixture passes the five mechanics; one failing case per rule, written by the test itself, each asserting the expected message. The existing `proposal-with-defects.md` fixture gains the assignment's sections in order and a body within the word bounds, and three of its twelve planted defects, the ones that named removed items (the missing smallest effect size, the t-test analysis, the condition-dependent exclusion), are replaced by three lens defects: the contributions written inline rather than as a bullet list (item 4.3), a reference list of 14 entries (item 5.1), and a consent form without the supervision sentence (item 12.3), so scenario 5 also exercises the draft checker; its answer key and its brief fixture lose their analysis and power entries and gain the three.

## Evaluation

Three runs per scenario, the bar holding only if all three meet it, recorded in the same evals folder with the plugin version and commit in each row. Records of 0.1.0 stay as evidence.

| Scenario                                        | Pass bar                                                                                                                                                                                                                                                                        |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2 `design` from material with planted gaps      | Every planted gap marked weak or missing; no settled decision asked again; the material and its key lose their analysis and power rows.                                                                                                                                         |
| 3 `design` from scratch on the text-entry idea  | Every design-tree item settled, provisional or pilot settles; item 8.5 justified by similar experiments and a reason from the sheet (which loses its analysis and power rows); the subagent consulted at least once; the checker passes on the brief; the freeze commit exists. |
| 5 `review` on the proposal with planted defects | At least 11 of the 12 defects caught and none passed, as the key scores them; the mechanics the draft checker reports (D3, D8 and D9); every draft-checked pass quotes evidence; picked fixes applied alone; missing-input stops; the checker passes on review.md.              |
| 6 Hand-off                                      | research-grill absent: the install commands, then the defend command, then the seed list; present: the exact command and the seed list; the final message ends with the hand-off in full.                                                                                       |
| Installs                                        | The delegation check (three runs, no unprompted delegation) and `claude plugin update` of the installed copy; the Codex copy updated and listed.                                                                                                                                |

Scenario 4 is deleted with the power group. The real-material check is an amendment session of `design` on the author's own project (`~/bloom-length-pilot`), resuming its frozen brief, retiring the power entries by amendment, and recorded under the evals folder with no bar; it exists to see the restructured skill on real material.

The implementation is done when the plugin tests and the repository checks pass, every scenario meets its bar, the real-material session is recorded, and the branch is merged into `main` with `git merge --ff-only` and pushed, with the tag `experiment-proposal--v0.2.0`.

## Bookkeeping

- The first spec gets `Disposition: superseded-by: 2026-10-14-experiment-proposal-v2-design.md` under its title; this spec is the current state. The sourcing register in the first spec keeps its rows as history; the verdicts for simr, statistical-power and the power template are retired here, each with its exit: stop using it, and nothing remains in the plugin.
- `plugin.json` version 0.2.0; after landing, `claude plugin tag` mints `experiment-proposal--v0.2.0` and the installed copies are updated in both tools and recorded.
- Issues: #222 closed as superseded by this spec; #223 to #230 closed by the branch with the commit that resolves each; #221 untouched.
- The evals folder keeps its name and gains the 0.2.0 run table; `docs/guides/experiment-proposal-guide.md` is unchanged (the guide keeps its step 11; the plugin's deviation says why it is not checked).

## Non-goals

- Powering any hypothesis; equivalence tests; the Planned Analysis section.
- Editing vendored text beyond marked frontmatter edits.
- Re-testing Codex session behaviour beyond the install update.
- A `draft` writer: the plugin never writes proposal prose.
- A second course's defaults: the mechanics are parameters, and only this course's values ship as defaults.

## Open risks

- **The checker against mdformat.** The brief and review are written by a model, not by mdformat; a user who runs mdformat over `proposal/` may reflow a table or escape a character the checker reads. The checker tolerates padding and escaped underscores; anything else is a defect the fixtures should catch early.
- **Word counting.** The body count depends on where the References heading sits and on tokenisation; the bounds are wide (2,000 to 4,000), and the checker reports the number, so a borderline draft is the user's call.
- **Reference counting.** A reference list written as a paragraph per entry or a numbered list counts the same; a list that mixes formats may miscount, and the checker prints what it counted.
- **The restructured prose.** A step file half the size may lose a behaviour the evals never named; the three-run bars and the real-material session are the net.
