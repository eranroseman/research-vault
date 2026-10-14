# Design: experiment-proposal, a plugin for designing and reviewing an experiment proposal

Date: 2026-10-13. Status: approved in brainstorming, awaiting spec review. Branch: `experiment-proposal-plugin`.

**Outside the assembly decomposition.** The plugin lies outside the decomposition in `docs/superpowers/specs/2026-09-05-assembly-design.md`, and this spec does not occupy the single active-spec slot that document's decision 22 allows.

## Goal

Help one researcher, the author, plan a controlled HCI experiment with human participants and check the written proposal before defending it. The process comes from the guide *How to Write an Experiment Project Proposal*: 13 steps, each ending in a **Done when** list. The plugin settles the design decisions first, freezes them in a brief, and then checks the draft against the brief and against a checklist derived from the guide.

The plugin is a second Claude Code plugin, `experiment-proposal`, in this repository's marketplace. It is independent of the research-vault plugin: it uses none of research-vault's skills, hooks, CLI or vault, and research-vault's skills do not route to it. research-vault's own skills are out of scope here.

## Evidence behind the design

A survey (2026-10-12 to 2026-10-13) compared 167 verified agent skills with the guide. No skill implements the 13 steps end to end; each covers a slice. Five findings shaped the design:

- The HCI researcher (K-Dense-AI's human-computer-interaction-researcher) is the only HCI-calibrated skill. It supplies judgment rather than eliciting decisions or drafting text.
- No verified skill elicits a session estimate that counts conditions (step 2). The one skill that treats counterbalancing at lab-experiment grade (step 7), cognitive-paradigm-design, is written for cognitive psychology rather than HCI.
- research-grill is the only verified defend stage aimed at a proposal, and it is licensed CC BY-NC 4.0.
- proposal-lit-search is the strongest step-5 search mechanism. (That its `SKILL.md` is bound to its thesis workflow comes from the screening read at `a38b7b11`, not from the survey.)
- statistical-power's simulation route covers random-intercept linear mixed models only.

The survey's three files are this spec's evidence siblings: the [sourcing-screen evidence](2026-10-13-experiment-proposal-plugin-design-sourcing-screen-evidence.md), the [rejected skills](2026-10-13-experiment-proposal-plugin-design-rejected-skills-evidence.md) and the [repository snapshot](2026-10-13-experiment-proposal-plugin-design-repositories-evidence.md). They carry two corrections to the original survey: statistical-power simulates random-intercept linear mixed models only, and the HCI researcher's repository README and `CITATION.cff` ask to be cited. The survey names the guide instead of linking it.

## Decisions

The table records the brainstorming decisions. Where this spec settles something they left open, it says *resolved here*.

| Question          | Decision                                                                                                                                                                                                                                  |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Users             | The author only, for now.                                                                                                                                                                                                                 |
| Packaging         | A second plugin at `plugins/experiment-proposal/`, marketplace source `"./plugins/experiment-proposal"`, install id `experiment-proposal@research-vault`. Independent of the research-vault plugin.                                       |
| Skills            | Four, each invoked by name only: `design` and `review` (ours), `lit-search` (our `SKILL.md` over vendored scripts), `the-ethics-board` (vendored). Two small skills rather than one skill with modes; a name-only skill costs no context. |
| Commands          | `/experiment-proposal:design`, `/experiment-proposal:review`, `/experiment-proposal:lit-search`, `/experiment-proposal:the-ethics-board`.                                                                                                 |
| Analysis default  | Mixed-effects models in R on trial-level data: lme4 `lmer` for continuous outcomes, `glmer` binomial for trial-level errors, ordinal `clmm` for ordinal ratings.                                                                          |
| Power             | Simulation in R from the plugin's template: simr for `lmer` and `glmer`, our own loop for `clmm`. A missing R prerequisite blocks the participant-count item loudly.                                                                      |
| statistical-power | Not vendored. Its effect-size sourcing ranking and sensitivity range become checklist items, restated and credited.                                                                                                                       |
| HCI judgment      | The HCI researcher, vendored as a subagent.                                                                                                                                                                                               |
| Defend stage      | research-grill, a separate install; no plugin dependency is declared.                                                                                                                                                                     |
| Checklist         | The plugin's own `references/checklist.md`, derived from the guide's Done-when lists with the deviations built in. The skills do not read the guide.                                                                                      |
| Artifacts         | A `proposal/` folder at the project root holding `design-brief.md`, `review.md` and `power.R`.                                                                                                                                            |
| The guide         | Copied into research-vault as documentation; that copy becomes the master, and the Backchat copy is deleted after the merge.                                                                                                              |
| Codex             | Claude Code first, Codex best-effort, with a recorded install test.                                                                                                                                                                       |
| Versioning        | The version lives only in the plugin's `plugin.json`, starting at 0.1.0; each release adds a tag.                                                                                                                                         |

## Sourcing screen

**The bounded question.** For one author planning a controlled HCI experiment by the guide's process, which existing skill, agent or tool can carry each of seven parts — design elicitation, proposal review, literature search, ethics rehearsal, HCI judgment, power analysis and the defend stage — and which parts must be built?

**The musts**, fixed before screening. The survey gathered the candidates and rated them on coverage alone; the screen then applied these musts to the entries the survey recorded.

| #   | Applies to         | Must                                                                                                                                                                                              |
| --- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| M1  | every part         | Its licence permits copying it into an MIT-licensed plugin, or it works as a separate install.                                                                                                    |
| M2  | every part         | It runs standalone, needing no other skill's workflow, state or files.                                                                                                                            |
| M3  | design elicitation | It elicits every HCI design decision of a controlled experiment, including within- or between-subjects with a reason, counterbalancing and the session estimate.                                  |
| M4  | design elicitation | Given existing material, it extracts the decisions already made and asks only about the rest.                                                                                                     |
| M5  | design elicitation | It records each decision with the user's rationale in a file.                                                                                                                                     |
| M6  | proposal review    | It checks every draft-checked item (see The checklist) derived from the guide's Done-when lists against the draft, and quotes the passage, with its location, that satisfies each item it passes. |
| M7  | proposal review    | It proposes a fix for each failure and applies only the fixes the user picks.                                                                                                                     |
| M8  | literature search  | Standalone, it searches several scholarly indexes, snowballs, and stops when a round adds nothing.                                                                                                |
| M9  | ethics rehearsal   | It rehearses an ethics review of a study with human participants.                                                                                                                                 |
| M10 | HCI judgment       | It answers HCI design questions: random-effects structure, counterbalancing scheme, validity threats and effect-size assumptions.                                                                 |
| M11 | power analysis     | It simulates power for linear and binomial mixed models with random slopes.                                                                                                                       |
| M12 | defend stage       | It puts a reviewer's objections about a proposal to the researcher, who settles each one.                                                                                                         |

Ordinal (`clmm`) power comes from our own loop in `templates/power-simr.R`, not from simr; the template is recorded among the verdicts.

**The candidates** are the 167 verified skills — the closest and partial matches of the [sourcing-screen evidence](2026-10-13-experiment-proposal-plugin-design-sourcing-screen-evidence.md) and the rejected skills of its [rejected-skills sibling](2026-10-13-experiment-proposal-plugin-design-rejected-skills-evidence.md) — the skills that sibling records as read only at heading level, and, for power analysis, the R package simr.

**Recorded exclusions**, by the must each candidate fails:

- **Design elicitation (M3).** No verified skill elicits a session estimate that counts conditions, so every candidate fails M3; the closest also fall short as follows. The HCI researcher supplies judgment rather than eliciting decisions, so it is adopted for M10 instead. proposal-write has no counterbalancing and no power calculation. research-grill's design tree serves survey and conjoint work, with no counterbalancing, within-subjects design, session estimate or pilot. cognitive-paradigm-design is written for cognitive-psychology paradigms, and its frontmatter requires a sibling skill (M2). luwill research-proposal and hypothesis-building have no within- or between-subjects choice and no counterbalancing. K-Dense-AI experimental-design frames designs around plates, batches and mice, with no human-subjects session. K-Dense-AI hypothesis-generation has no counterbalancing scheme and no rule for choosing within- or between-subjects. pre-registration-writing routes design to sibling skills (M2). alterlab-test-selection-guard selects tests only, and alterlab-research-ethics touches design only as one-line IRB-template prompts. Diverga c1 opens with an MCP prerequisite gate and references files its mirror does not contain (M2). experiment-agent runs only inside academic-research-suite (M2) and has no counterbalancing.
- **Proposal review (M6).** The Done-when items are the guide's own, so no candidate checks them; the closest check other lists. proposal-review and proposal-supervise review a thesis proposal against their own criteria. research-grill runs a defend stage, not an item-by-item check; it is adopted for M12. alterlab-thesis-supervisor carries a defense checklist for generic theses. methods-reporting audits against a 45-item reporting checklist, 13 of whose items apply only after data collection and none of which covers counterbalancing, condition order, session length or consent. review-pap reviews an economics pre-analysis plan, and thesis-examiner a finished thesis.
- **Literature search (M8).** No candidate both runs standalone and searches, snowballs and stops as M8 requires. proposal-lit-search, the strongest search mechanism, meets the search half but not the standalone half: its `SKILL.md` (read at `a38b7b11`) merges accepted sources into its own proposal's `references:` block as one step of its thesis workflow. Its scripts are not bound to that workflow, and they are adopted. scriptorium review, synthesize and contradictions run in Claude Cowork as stages of one pipeline whose search phase needs scholarly-search MCP connectors (M2). leiverkus literature-review wraps a skill its repository does not ship (M2). luwill research-proposal collects literature only as a phase of its own proposal workflow (M2). proposal-write drafts from the references already in its proposal (M8).
- **Literature search, read on 2026-10-13.** K-Dense-AI literature-review (at `a92663a0`) leaves citation chaining to a sibling skill, parallel-web (M2), and has no stop rule for a round that adds nothing (M8). alterlab-thesis-supervisor (at `619954a3`) routes literature search to a sibling skill (M2). K-Dense-AI surveying-prior-work (at `8c5f9d78`) requires a sibling skill for broad surveys (M2). Imbad0202's deep-research (at `a3ef8c79`) has no snowballing or stop rule (M8). scdenney literature-review (at `697c89ff`) runs standalone but works from the sources the user supplies, with no index search, snowballing or stop rule (M8).
- **Ethics rehearsal (M9).** ethics-review, irb-protocol, research-ethics, writing-irb-submissions and alterlab-research-ethics draft or check protocol and consent material; none rehearses a review. the-ethics-board, a simulated ethics committee, is adopted.
- **Power analysis (M11).** statistical-power simulates random-intercept linear mixed models only: no random slopes and no binomial outcomes. cogsci-power-analysis gives guidance and runs no code.
- **The rest.** The rejected-skills sibling rates its skills, at full or heading level, on coverage alone and names no must. The findings that open the design and review bullets exclude them all, and by their recorded reasons none of them searches the literature (M8) apart from those named above.

**Verdicts.** Every row was decided in this spec. Each exit says what remains if the component goes away; a component that writes nothing, or was never installed, says so.

| Component         | Verdict                                       | Tier           | floor_failed | decided_in | The exit                                                                                                                                                       |
| ----------------- | --------------------------------------------- | -------------- | ------------ | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| design            | build                                         | prompt-bearing | M3           | this spec  | Stop invoking it; `proposal/design-brief.md` stays ordinary Markdown.                                                                                          |
| review            | build                                         | prompt-bearing | M6           | this spec  | Stop invoking it; `proposal/review.md` stays ordinary Markdown.                                                                                                |
| lit-search        | adapt (scripts adopted, `SKILL.md` rewritten) | prompt-bearing | M8           | this spec  | Stop invoking it; it writes nothing, and the sources kept are in the draft.                                                                                    |
| the-ethics-board  | adopt (skill)                                 | prompt-bearing | —            | this spec  | Stop invoking it; it writes nothing.                                                                                                                           |
| HCI researcher    | adopt (subagent)                              | prompt-bearing | —            | this spec  | Stop invoking it; the answers recorded in the brief stay ordinary Markdown.                                                                                    |
| simr              | adopt (user-installed)                        | mature tool    | —            | this spec  | Stop invoking it; the participant count and power curve in the brief stay ordinary Markdown, and `proposal/power.R` stays readable R that needs simr to rerun. |
| power template    | build (simr cannot simulate `clmm`)           | glue           | —            | this spec  | Stop using it; each project's filled `proposal/power.R` stays.                                                                                                 |
| statistical-power | reject (fails M11)                            | prompt-bearing | —            | this spec  | Never installed; nothing remains.                                                                                                                              |
| research-grill    | adopt (separate install)                      | prompt-bearing | —            | this spec  | Stop invoking it; what it wrote stays ordinary Markdown.                                                                                                       |

No component register file exists. The verdicts are recorded only here, as `docs/superpowers/specs/2026-09-17-pre-lane-2-design.md` §5.1 recorded its own.

## Plugin layout

```text
plugins/experiment-proposal/
  .claude-plugin/plugin.json     name, description, version (0.1.0)
  LICENSE                        MIT, Copyright (c) 2026 Eran Roseman
  THIRD-PARTY-NOTICES.md         MIT text and copyright line of every vendored or adapted source
  README.md                      install, commands, prerequisites, citation requests
  references/
    checklist.md                 Done-when items for all 13 steps, deviations built in
  templates/
    power-simr.R                 lmer and glmer power through simr; a simulation loop for clmm
  agents/
    hci-researcher.md            vendored subagent, renamed hci-researcher
  skills/
    design/
      SKILL.md
      agents/openai.yaml
    review/
      SKILL.md
      agents/openai.yaml
    lit-search/
      SKILL.md                   ours
      agents/openai.yaml
      scripts/                   nine vendored Python scripts
    the-ethics-board/
      SKILL.md                   vendored, one marked frontmatter edit
      agents/openai.yaml
```

Every `SKILL.md` sets `disable-model-invocation: true` in its frontmatter, and every `agents/openai.yaml` sets `allow_implicit_invocation: false` under `policy`. `design` and `review` write into the user's project:

```text
proposal/
  design-brief.md    the frozen design decisions; records the draft's path
  review.md          the checklist result, one row per item
  power.R            the filled power template
```

## design

**Start.** First, `design` checks its prerequisites (see R and power). Given paths to existing material, it extracts the decisions already made and marks each design-tree item settled, weak or missing, then questions the user only on weak and missing items. Given only an idea, it starts from scratch.

**The design tree** is the design items of `references/checklist.md`:

| Step | Design items                                                                                                                                                                                                                                                                             |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | The question; the ethics route; the data plan.                                                                                                                                                                                                                                           |
| 2    | The session estimate; the pilot; the timeline; expected challenges.                                                                                                                                                                                                                      |
| 6    | Each hypothesis's direction; the smallest effect size of interest, with equivalence tests for "no worse" hypotheses; a support, falsify or inconclusive decision rule per hypothesis.                                                                                                    |
| 7    | Variables and their operational definitions; within- or between-subjects, with reasons; carry-over; random assignment; counterbalancing; controls; confounds.                                                                                                                            |
| 8    | Eligibility; a justified participant count.                                                                                                                                                                                                                                              |
| 11   | The mixed-model plan: trials as the unit of analysis; the model family per dependent variable; fixed effects and contrast coding; random effects, with a pre-specified simplification order for non-convergence; the inference method; exclusions and trimming; the multiplicity policy. |

**Item statuses.** Extraction marks each item *settled*, *weak* or *missing*. A round leaves each item it asks about *settled* (the user decided), *pilot settles* (the user decided the pilot will set the value) or *provisional* (the user could not answer, so the recommendation stands in). The participant-count item (step 8) is *BLOCKED* while an R prerequisite is missing, and *waived* once the user records a reason the count is justified without a power analysis.

**Rounds.** The frontier-rounds mechanic is adapted, in our own words, from Matt Pocock's grilling skill (mattpocock/skills, MIT) and credited. Each round asks every question whose dependencies are settled, numbers them, and waits; the checklist records which items each item depends on. Each question carries:

- the question in plain language, with any technical term glossed once;
- a "why this matters" line;
- a recommended answer that cites the checklist item or a source.

Facts are looked up, not asked; decisions are the user's. When the user cannot answer an item, its recommendation is recorded as provisional and the round moves on. Three ideas from research-grill are restated, with no CC BY-NC text: the "why this matters" line, provisional answers, and a written record.

**Consulting the HCI researcher.** `design` sends the `hci-researcher` subagent specific questions: the random-effects structure, the counterbalancing scheme, validity threats and effect-size assumptions.

**Other skills.** `design` cannot invoke `lit-search` or `the-ethics-board`, which are name-only. It lists the need as an open item and tells the user which command to run.

**The brief** holds one entry per settled or "pilot settles" item — the decision, the rationale in the user's words, what would change it, its status and its source — followed by a Looked up section (fetched facts with their sources) and an Open items section. Open items lists the BLOCKED or waived participant-count item first, with the waiver's reason if there is one, then each provisional item with its recommendation, then each command `design` asks the user to run. The brief also records the draft's planned path.

**Done when:** no item is weak, missing or BLOCKED: every design-tree item is settled, "pilot settles", or provisional and listed under Open items, or, for the participant-count item, waived; the user approves the brief; and, with the user's OK, the skill commits it. That commit is the freeze record.

**Changing a frozen brief** (resolved here). Frozen entries are never edited. To change a decision, the user re-runs `design`, which appends a dated entry to an Amendments section — the item, the new decision and the reason — and commits it with the user's OK. If the user names a different draft at review time, `review` notes that path in `review.md`; the brief is unchanged.

## review

**Inputs.** `review` reads `proposal/design-brief.md`, the draft at the path the brief records (or one the user names), and the checklist. If the brief or the draft is missing, it stops and says which.

**Checks:**

- every checklist item of all 13 steps, apart from the two the defend stage takes over (see The checklist): a draft-checked item passes with the quoted passage and its location, and an attested item with the user's confirmation, which `review` records in `review.md`; a fail says what is missing;
- step 11 as the checklist's deviations rewrite it: a mixed model that matches the design satisfies the guide's "named test";
- cross-section consistency: participant counts, durations and variable names are identical wherever they appear;
- brief against draft: every departure from the frozen brief and its amendments is flagged;
- six substance tests, borrowed as ideas from hutzelmann's proposal-supervise (MIT): delta, falsifiability, swap, necessity, method fit and executability.

**Output.** `proposal/review.md` holds one row per item: pass or fail, the quote and its location (or the user's confirmation), and for each failure a proposed fix, either replacement text or the decision needed. Summary counts close it. The user picks fixes by number; `review` applies only those and re-checks the affected items.

**Done when:** every item `review` checks passes, or fails with a user-accepted waiver recorded with its reason in `review.md`.

**Hand-off to the defend stage.** `review` ends by printing the exact command `/oss:research-grill defend <draft path>` and a seed list of objections: the remaining waivers; "could someone run a session from the Method alone?"; and any substance test passed narrowly, meaning one whose pass `review` recorded with a doubt the draft could not settle. If research-grill is not installed, `review` says so and gives the install commands in place of the defend command (`claude plugin marketplace add scdenney/open-science-skills`, then `claude plugin install oss@open-science-skills`). The plugin declares no dependency on research-grill, because a declared dependency would auto-install its noncommercial code.

## The checklist

`references/checklist.md` is derived from the guide's Done-when lists, at Backchat commit `98b978f`, with the deviations built in. Its provenance note names that source and commit. The skills read only the checklist, never the guide.

Each item carries an ID, which `design`'s recommendations and `review`'s rows cite and the plugin tests check. Each item also lists the items it depends on, which order `design`'s rounds, and its kind: *draft-checked* when the draft can show it, or *attested* when it concerns the process rather than the text, such as step 5's "Snowballing ... has stopped turning up new relevant work".

The deviations, listed in the checklist:

- Mixed models replace the guide's step-11 test table and rewrite step 11's Done-when items. Trials are the unit of analysis, so the item on reducing trial-level data to the values tested asks instead for the unit of analysis and any aggregation. The model family per dependent variable, its fixed effects and contrast coding, and its random effects with a pre-specified simplification order replace the named test, its non-parametric alternative and the rule for choosing between them. The sphericity check is dropped, since mixed models do not assume sphericity. Exclusions gain trimming, and the significance level gains the inference method and the multiplicity policy. Step 2's "test for each hypothesis" becomes the model for each hypothesis.
- `lit-search` replaces step 5's search tips.
- research-grill's defend stage replaces "present to a critical listener" in step 13, and its written record serves the feedback item that follows. `review` checks neither item; it hands off to the defend stage.
- Additions:
  - the smallest effect size of interest, and equivalence tests for "no worse" hypotheses;
  - a support, falsify or inconclusive decision rule per hypothesis;
  - a dry run of the analysis script on simulated data;
  - the effect-size sourcing ranking and the sensitivity range, restated from statistical-power (MIT) and credited;
  - the six substance tests.

## R and power

**Prerequisites.** At session start, `design` checks for `Rscript` and the R packages lme4, lmerTest, ordinal and simr. If any is missing, it:

1. reports exactly what is missing, with install commands;
2. marks the participant-count item BLOCKED, not pending, and lists it first under Open items;
3. refuses to freeze the brief unless the user records a waiver there: a stated reason the participant count is justified without a power analysis, which the guide's step 8 allows.

`review` reads the waiver from the brief and fails a BLOCKED participant-count item that has none. Every other missing prerequisite gets a clear stop with its install command, never a silent skip: `lit-search` stops without Python 3.11 or later, and `review`'s hand-off, without research-grill, gives the install commands in place of the defend command.

**The template.** `templates/power-simr.R` is our own code. It covers `lmer` and `glmer` through simr and carries its own simulation loop for `clmm`, which simr does not support. At the participant-count item, `design` fills the template from the brief into `proposal/power.R`, asks the user's OK to run it, runs it with `Rscript`, and records the resulting participant count and power curve in the brief. The primary measure's model sets the participant count, and the other models' power at that count is reported beside it (resolved here).

simr (GPL), lme4, lmerTest and ordinal are installed by the user from CRAN; none is vendored.

## lit-search

Its `SKILL.md` is ours and short: search across Crossref, OpenAlex, DBLP, arXiv, Semantic Scholar and OpenCitations; snowball; keep a source only if the claim it supports can be named; stop when a round adds nothing. It runs the nine scripts of hutzelmann/thesis-proposal-skills `skills/proposal-lit-search/scripts/*.py` (upstream), which need Python 3.11 or later and only the standard library; the skill checks the version first. The scripts print CSL-YAML and write no files, and `lit-search` writes none either: it reports each kept source, with the claim it supports, for the user to add to the draft. Upstream's `evals/evals.json` is not copied, because its fixture is missing upstream. The scripts still identify themselves to the APIs as the upstream project; that is accepted. `OPENALEX_API_KEY` is optional, and OpenAlex is skipped without it; `CONTACT_EMAIL` is read when set.

## Vendoring, licensing and attribution

A vendored file may differ from upstream only by its provenance header, by mdformat normalization (Markdown only), and by edits marked as local.

- **K-Dense-AI/scientific-agents** (MIT, K-Dense Inc.; read at `98c7fae4`): the subagent `scientific-agents/human-computer-interaction-researcher/agents/human-computer-interaction-researcher.md` becomes `agents/hci-researcher.md`. Its frontmatter `name` changes from `human-computer-interaction-researcher` to `hci-researcher`, a marked local edit, and `design` calls it by that name.
- **hutzelmann/thesis-proposal-skills** (MIT, hutzelmann; read at `a38b7b11`): the nine upstream scripts `skills/proposal-lit-search/scripts/*.py` become the `lit-search` skill's `scripts/`.
- **mohitagw15856/pm-claude-skills** (MIT, Copyright (c) 2026 Mohit Aggarwal; read at `f93fee74`): the upstream `skills/the-ethics-board/SKILL.md` keeps its path, with one marked local frontmatter edit, `disable-model-invocation: true`. The file names no licence, so the notices carry the repository's LICENSE text.
- **mattpocock/skills** (MIT, Copyright (c) 2026 Matt Pocock; read at `49dd158d`): the frontier-rounds mechanic of the grilling skill (upstream `skills/productivity/grilling/SKILL.md`), adapted in our own words into the `design` skill and credited. research-grill credits a different skill of his, grill-me.

research-grill was read at open-science-skills `cd70e9b4` and is not copied.

**Provenance headers.** Every vendored file carries research-vault's header, in the Markdown form of `skills/find-sources/references/crossref.md` (an HTML comment) or the Python form of `skills/find-sources/scripts/paginate.py` (`#` comment lines after the shebang). The header names the upstream URL, the full 40-character commit sha, the upstream path, and the licence and copyright; adds a rename note naming the experiment-proposal plugin wherever a path or name changed; and ends "Do not hand-edit this file; re-vendor from upstream to update it." The pin is the commit read during screening, listed above; vendoring a newer commit means re-reading the files at it first.

Two additions to that precedent are resolved here. The header of a vendored Markdown file says that mdformat normalized it. In a file that must open with YAML frontmatter (the-ethics-board's `SKILL.md` and the subagent), the header follows the frontmatter, as the Python form follows the shebang.

**Licence files.** `plugins/experiment-proposal/LICENSE` is MIT, Copyright (c) 2026 Eran Roseman. `plugins/experiment-proposal/THIRD-PARTY-NOTICES.md` carries the full MIT text and the copyright line of K-Dense Inc., Mohit Aggarwal, hutzelmann and Matt Pocock. Both live inside the plugin folder, because a subdirectory install does not ship the repository's root LICENSE. The plugin README notes, neutrally, that the scientific-agents README and `CITATION.cff` (both at `98c7fae4`) and the pm-claude-skills `CITATION.cff` (at `f93fee74`) ask to be cited.

**ATTRIBUTION.md** gains index entries:

- under Adopted components, a row each for simr (GPL; installed by the person from CRAN, never by this repository) and research-grill (CC BY-NC 4.0; a separate install), each with its exit line;
- under Vendored source, a paragraph for each copied source: scientific-agents, thesis-proposal-skills and pm-claude-skills;
- a new "Adapted into `plugins/experiment-proposal/`" paragraph after the paper-critical-analysis one, with a one-row copyright table for Matt Pocock's grilling text in the `design` skill, closed, like that paragraph's Imbad0202 sentence, by the ideas-only credits: proposal-supervise (the substance tests), statistical-power (the effect-size ranking and sensitivity range) and research-grill (the "why this matters" line, provisional answers, the written record);
- a note for the guide: adapted from the Research Methods in HCI course materials (the project assignment and the course methods guide), its test table aligned with UCLA OARC's test-selection table; restated, not quoted;
- an amendment to its opening note, which puts each provenance header "at the top of the file", allowing for a header that follows YAML frontmatter.

## research-vault integration

**Marketplace.** `.claude-plugin/marketplace.json` gains one entry: name `experiment-proposal`, source `"./plugins/experiment-proposal"`, a one-line description like the existing entry's, and no version. The file stays in its canonical JSON form: `json.dumps` with `indent=2` and `ensure_ascii=False`, plus a trailing newline.

**Versioning.** The version lives only in the plugin's `plugin.json`, starting at 0.1.0. Each release bumps it and adds the git tag `experiment-proposal--v<version>`, Claude Code's convention.

**Tests.** A plugin-scoped test file, `tests/test_experiment_proposal_plugin.py` (planned), checks that:

- `plugin.json` is valid and canonical; the marketplace entry's name equals its name, and the entry's source resolves to the folder that holds the plugin's `.claude-plugin/plugin.json`;
- every `SKILL.md` has `name`, `description` and `disable-model-invocation: true`, and a Codex `agents/openai.yaml` with `allow_implicit_invocation: false`;
- every vendored file has a full provenance header;
- `THIRD-PARTY-NOTICES.md` lists every copyright holder;
- every checklist item the skills cite exists;
- the `lit-search` scripts compile;
- the R template parses where `Rscript` exists; where it does not, the test reports SKIPPED, never a pass.

The repository's own skill tests glob only the root `skills/` directory and do not cover the plugin. The repository-wide checks do: mdformat, home-directory paths, Disposition values and table code spans. No `research_vault` Python module changes, so the mutation gate has nothing to run. `CONTEXT.md` stays untouched, because it is copied into user vaults.

**Git.** All work is on branch `experiment-proposal-plugin`, committed with explicit pathspecs. The author pushes the branch. When the required quality check is green, the branch is merged into `main` with `git merge --ff-only` and `main` is pushed.

## Codex

Claude Code comes first; Codex is best-effort. The plan includes a Codex install test that records the known gaps:

- Codex reads Claude marketplaces in a legacy-compatible mode.
- It ignores plugin dependencies.
- It sets `${CLAUDE_PLUGIN_ROOT}` only for hooks.
- It reads `agents/openai.yaml` instead of `disable-model-invocation`.
- Its handling of plugin-bundled subagents is undocumented.

**Fallback.** If `${CLAUDE_PLUGIN_ROOT}` does not resolve in Codex skill text, the checklist moves to `plugins/experiment-proposal/skills/review/references/checklist.md`. `review` then reads `references/checklist.md` relative to its own folder, and `design` reads `../review/references/checklist.md` relative to its own; both skills ship in one plugin folder, so they sit side by side. The template has the same problem, and the fallback moves it too, to `plugins/experiment-proposal/skills/design/templates/power-simr.R` (resolved here).

## Evals

The records go in `docs/research/2026-10-13-experiment-proposal-evals/` (planned): a README with a run table and one record per run. Every answer key is written before any run. Each scenario runs three times, and its pass bar holds only if all three runs meet it.

| Scenario                                                                          | Pass bar                                                                                                                                                                                                                                                                                                                                                         |
| --------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Baseline: no plugin, the mouse-versus-trackball idea                              | None; the runs record the failures (the RED step).                                                                                                                                                                                                                                                                                                               |
| `design` from material with planted gaps                                          | Every planted gap is marked weak or missing; no settled decision is asked again.                                                                                                                                                                                                                                                                                 |
| `design` from scratch on a within-subjects text-entry idea with an ordinal rating | Every design-tree item is settled, provisional or "pilot settles"; the mixed-model plan is complete; power is computed, the rating's through the `clmm` loop; `design` consults the subagent at least once; the freeze commit exists.                                                                                                                            |
| `design` with no R                                                                | The participant-count item is BLOCKED with install commands; the brief does not freeze until the user records a waiver.                                                                                                                                                                                                                                          |
| `review` on a proposal with 12 planted defects                                    | At least 11 caught and none passed: a defect is caught when the item the answer key names fails, and passed when that item is marked pass. Every draft-checked pass quotes evidence. When the user picks two fixes by number, `review` applies only those and re-checks the affected items. With the brief or the draft removed, `review` stops and names which. |
| Hand-off                                                                          | With research-grill missing, a clear install message; otherwise the exact command and the seed list.                                                                                                                                                                                                                                                             |
| Installs                                                                          | Claude Code from git: namespaced names, name-only invocation, the subagent available, the checklist path resolving. Codex: the gaps recorded; if a Codex session cannot open the checklist through `${CLAUDE_PLUGIN_ROOT}`, the fallback is applied and the install test run again.                                                                              |

`lit-search` has no scenario; the compile check in the plugin tests is its only test.

**The implementation is done when** the plugin tests and the repository checks pass, every scenario meets its pass bar, and the branch is merged into `main` with `git merge --ff-only` and pushed.

## The Backchat side

**The guide.** Backchat's *How to Write an Experiment Project Proposal* is copied to `docs/guides/experiment-proposal-guide.md` (planned) as documentation the skills do not read. The kebab-case name is required: a space in a file name breaks the mdformat hook and the dangling-path test. The research-vault copy becomes the master, and the Backchat copy is deleted after this branch merges, by Backchat's rule that superseded documents are deleted and git history keeps them.

**The survey.** Its three files become this spec's evidence siblings, with the two corrections above. Backchat's copies (`docs/research/agent-skills-for-experiment-proposals*.md`) and the then-empty `docs/research/` are deleted after this branch merges.

**Follow-up.** These deletions are Backchat work, tracked as a Backchat issue (planned) once this branch merges; they are not steps of this branch's plan.

## Non-goals

- "Build a new tech" projects: formative interviews, design requirements, a system.
- Any research-vault skill, hook or CLI.
- statistical-power.
- Skills that read the guide.
- One skill with modes.
- A declared plugin dependency on research-grill.
- Moving the critical-analysis guide, which stays in Backchat.

## Open risks for the install tests

- **`${CLAUDE_PLUGIN_ROOT}` in skill text.** The checklist and template paths must resolve in Claude Code; in Codex they may not, which triggers the fallback.
- **The bundled subagent.** Claude Code must expose `agents/hci-researcher.md` to `design`; Codex's handling is undocumented. Unlike a name-only skill, a subagent's description loads into every session where the plugin is enabled, and Claude may delegate to it unprompted; the install test records both.
- **Name-only invocation.** `disable-model-invocation` must hold in Claude Code, and `agents/openai.yaml` in Codex.
- **Headers after frontmatter.** Both hosts must still parse the frontmatter of a vendored `SKILL.md` or agent file whose provenance header follows it.
- **Detecting research-grill.** `review` must be able to tell whether research-grill is installed before it prints the hand-off.
- **Codex marketplace reading.** The legacy-compatible mode must find a plugin whose source is a subdirectory.
