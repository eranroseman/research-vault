# experiment-proposal

A Claude Code plugin for one researcher writing the course's experiment proposal: settle the design decisions first and freeze them in a brief, then check the written draft against the brief, a checklist and the template's mechanics before defending it. The checklist (`references/checklist.md`) derives from the Done-when lists of *How to Write an Experiment Project Proposal* (the research-vault repository's `docs/guides/experiment-proposal-guide.md`), judged by the assignment the proposal is written for; the skills read the checklist, never the guide.

The plugin is independent of the research-vault plugin in the same marketplace: it uses none of its skills, hooks, CLI or vault.

## Install

```bash
claude plugin marketplace add eranroseman/research-vault
claude plugin install experiment-proposal@research-vault
```

Start a new session after installing; plugins load at session start. Codex reads the same marketplace in a legacy-compatible mode (`codex plugin marketplace add eranroseman/research-vault`, then `codex plugin add experiment-proposal@research-vault`); Claude Code comes first and Codex is best-effort, with the known gaps recorded in the repository's evaluation records.

## What it produces

Your proposal, written by you, in the assignment's shape: the sections Introduction, Literature review, Research questions or Hypotheses, Participants, Materials, Procedure, Design and Appendix, in that order; 2,000 to 4,000 words excluding references and appendices; 15 to 20 references; a bullet list of contributions in the Introduction; and a consent form in the appendix that states the study is "under the supervision of" your instructor. Those are the defaults; `review` asks you to confirm or change them at checklist item 3.1, and the checker (`scripts/check_proposal.py draft`) measures them.

## Commands

Every skill is invoked by name only; none is picked up by the model on its own.

| Command                                 | What it does                                                                                                                                                                                                                                                                     | Writes                                                   |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| `/experiment-proposal:design`           | Extracts the decisions your material already makes, asks the rest in numbered rounds with a recommendation per question, consults the HCI-researcher subagent on counterbalancing and validity, writes the brief, runs the checker, freezes by commit.                           | `proposal/design-brief.md`, committed with your OK       |
| `/experiment-proposal:review`           | Confirms the template's mechanics and runs the draft checker, checks every checklist item (a quoted passage per pass), cross-section consistency, the brief and six substance tests; proposes a fix per failure; applies only the fixes you pick; hands off to the defend stage. | `proposal/review.md`, and the draft for the fixes picked |
| `/experiment-proposal:lit-search`       | Keyword-searches Crossref, OpenAlex, DBLP, arXiv and Semantic Scholar, snowballs through Semantic Scholar, OpenAlex, Crossref and OpenCitations, keeps a source only with the claim it supports, counts against the reference target, stops when a snowball round adds nothing.  | nothing                                                  |
| `/experiment-proposal:the-ethics-board` | Rehearses an ethics-committee review of the study: transcript, vulnerability map, revision list.                                                                                                                                                                                 | `proposal/ethics-review.md` (its review)                 |

The order is `design` first, then your draft at the path the brief records (`proposal/draft.md` by default), then `review`; run `lit-search` and `the-ethics-board` whenever the brief's Open items ask for them.

The subagent `hci-researcher` ships with the plugin, restricted to reading; `design` consults it on counterbalancing, control variables, validity threats and confounds. Its description is loaded into every session where the plugin is enabled.

## Prerequisites

- **git** in your project: `design` freezes the brief by commit.
- **Python 3.11 or later**, as `python3`, for the checker and for `lit-search`'s scripts; the skills stop with an install pointer when it is older. `lit-search`'s keys are optional: `OPENALEX_API_KEY` (OpenAlex is skipped without it) and `CONTACT_EMAIL` are read from the environment or from a key file (`api-keys.env` in the working directory, or `~/.config/thesis-proposal/api-keys.env`), `OPENCITATIONS_TOKEN` from the environment only; a Semantic Scholar key is not used. Your search terms and seed DOIs go to those public APIs.
- **research-grill** for the defend stage, a separate install this plugin does not declare as a dependency because it is licensed CC BY-NC 4.0: `claude plugin marketplace add scdenney/open-science-skills` then `claude plugin install oss@open-science-skills`. `review` prints these commands ahead of the defend command when it is absent.

## Headless use

The skills run under `claude -p` with `--permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)"`; compound shell commands are refused by the permission layer and the skills retry in an allowed form. A `design` run is several turns; use `--continue` for each answer.

## Artifacts and vendored behaviour

`design` writes `proposal/design-brief.md` (the decisions, each with your rationale, what would change it, its status and its source, plus Looked up, Open items and Amendments) and commits it with your OK. `review` writes `proposal/review.md` (one row per checklist item) and edits your draft, wherever the brief's `Draft:` line points, only for the fixes you pick. `the-ethics-board`, a vendored skill, writes its review to `proposal/ethics-review.md`; the researcher answers in its transcript are the simulation's, not yours, so check them against what you said. Stop using the plugin and every file stays ordinary Markdown.

## Licences and citations

The plugin is MIT licensed (`LICENSE`). It carries vendored and adapted material from four MIT-licensed sources, listed with their copyright lines in `THIRD-PARTY-NOTICES.md`. Two of those projects ask to be cited: K-Dense-AI/scientific-agents (its README and `CITATION.cff`, read at commit `98c7fae4`) and mohitagw15856/pm-claude-skills (its `CITATION.cff`, read at commit `f93fee74`); their citation files give the preferred forms.

## Version

The version has one writer, `.claude-plugin/plugin.json`; the brief's `Checklist:` line reads it from there. Each release is tagged `experiment-proposal--v<version>` in the research-vault repository.
