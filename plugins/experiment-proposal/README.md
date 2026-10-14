# experiment-proposal

A Claude Code plugin for one researcher planning a controlled HCI experiment with human participants: settle the design decisions first, freeze them in a brief, then check the written proposal against the brief and a checklist before defending it. The process follows the 13 steps of *How to Write an Experiment Project Proposal* (the research-vault repository's `docs/guides/experiment-proposal-guide.md`); the skills read the plugin's own `references/checklist.md`, derived from that guide's Done-when lists, with the deviations built in.

The plugin is independent of the research-vault plugin in the same marketplace: it uses none of its skills, hooks, CLI or vault.

## Install

```bash
claude plugin marketplace add eranroseman/research-vault
claude plugin install experiment-proposal@research-vault
```

Start a new session after installing; plugins load at session start. Codex reads the same marketplace in a legacy-compatible mode (`codex plugin marketplace add eranroseman/research-vault`, then `codex plugin add experiment-proposal@research-vault`); Claude Code comes first and Codex is best-effort, with the known gaps recorded in the repository's evaluation records.

## Commands

Every skill is invoked by name only; none is picked up by the model on its own.

| Command                                 | What it does                                                                                                                                                                                                                                                   | Writes                                                   |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| `/experiment-proposal:design`           | Checks the R prerequisites, extracts the decisions already made from material you name, asks the rest in numbered rounds with a recommendation per question, consults the HCI-researcher subagent, runs the power simulation, and freezes the brief by commit. | `proposal/design-brief.md`, `proposal/power.R`           |
| `/experiment-proposal:review`           | Checks the draft against every checklist item (a quoted passage per pass), cross-section consistency, the frozen brief and six substance tests; proposes a fix per failure; applies only the fixes you pick; hands off to the defend stage.                    | `proposal/review.md`, and the draft for the fixes picked |
| `/experiment-proposal:lit-search`       | Keyword-searches Crossref, OpenAlex, DBLP, arXiv and Semantic Scholar, snowballs from seed DOIs through Semantic Scholar, OpenAlex, Crossref and OpenCitations, keeps a source only with the claim it supports, and stops when a snowball round adds nothing.  | nothing                                                  |
| `/experiment-proposal:the-ethics-board` | Rehearses an ethics-committee review of the study: transcript, vulnerability map, revision list.                                                                                                                                                               | nothing                                                  |

The order is `design` first, then your draft at the path the brief records (`proposal/draft.md` by default), then `review`; run `lit-search` and `the-ethics-board` whenever the brief's Open items ask for them.

The subagent `hci-researcher` ships with the plugin; `design` consults it on the random-effects structure, the counterbalancing scheme, validity threats and effect-size assumptions. Its description is loaded into every session where the plugin is enabled.

## Prerequisites

- **R**, on `PATH` as `Rscript`, with the packages lme4, lmerTest, ordinal and simr, installed by you from CRAN (`Rscript -e 'install.packages(c("lme4","lmerTest","ordinal","simr"), repos="https://cloud.r-project.org")'`). Without them `design` marks the participant-count item BLOCKED, prints the install commands, and will not freeze the brief unless you record a waiver: a reason the count is justified without a power analysis. simr is GPL and is never vendored.
- **git** in your project: `design` freezes the brief by commit.
- **Python 3.11 or later** for `lit-search`; the skill stops with the install pointer when it is older. Keys are optional: `OPENALEX_API_KEY` (OpenAlex is skipped without it) and `CONTACT_EMAIL` are read from the environment or from a key file (`api-keys.env` in the working directory, or `~/.config/thesis-proposal/api-keys.env`), `OPENCITATIONS_TOKEN` from the environment only. Your search terms and seed DOIs go to those public APIs.
- **research-grill** for the defend stage, a separate install this plugin does not declare as a dependency because it is licensed CC BY-NC 4.0: `claude plugin marketplace add scdenney/open-science-skills` then `claude plugin install oss@open-science-skills`. `review` prints these commands in place of the defend command when it is absent.

## Artifacts

`design` writes `proposal/design-brief.md` (the frozen decisions, each with your rationale, what would change it, its status and its source, plus Looked up, Open items and Amendments) and `proposal/power.R` (the filled power template, plain R that needs simr to rerun), and commits the brief with your OK. `review` writes `proposal/review.md` (one row per checklist item) and edits your draft, wherever the brief's `Draft:` line points, only for the fixes you pick. Stop using the plugin and all three stay ordinary Markdown and R.

## Analysis defaults

Mixed-effects models on trial-level data: lme4 `lmer` for continuous outcomes, `glmer` binomial for trial-level errors, ordinal `clmm` for ordinal ratings. Power by simulation from `templates/power-simr.R`: simr for `lmer` and `glmer`, the template's own loop for `clmm`. The primary measure's model sets the participant count; the other models' power at that count is reported beside it.

## Licences and citations

The plugin is MIT licensed (`LICENSE`). It carries vendored and adapted material from four MIT-licensed sources, listed with their copyright lines in `THIRD-PARTY-NOTICES.md`. Two of those projects ask to be cited: K-Dense-AI/scientific-agents (its README and `CITATION.cff`, read at commit `98c7fae4`) and mohitagw15856/pm-claude-skills (its `CITATION.cff`, read at commit `f93fee74`); their citation files give the preferred forms.

## Version

The version lives in `.claude-plugin/plugin.json` (0.1.0); each release is tagged `experiment-proposal--v<version>` in the research-vault repository.
