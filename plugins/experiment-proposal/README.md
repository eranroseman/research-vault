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

Your proposal, written by you, in the assignment's shape: the sections Introduction, Literature review, Research questions or Hypotheses, Participants, Materials, Procedure, Design and Appendix, in that order; 2,000 to 4,000 words excluding references and appendices; 15 to 20 references cited in the Literature review; a bullet list of contributions in the Introduction; and a consent form in the appendix that states the study is "under the supervision of" your instructor. Those are the defaults; `review` asks you to confirm or change them at checklist item 3.1, and the checker (`scripts/check_proposal.py draft`) measures them.

The checker counts references as the Literature review's citations: a numbered list (`[1] ...` lines) by the numbers cited there, a number cited with no entry being a defect; any other list by each entry's first surname and year. The list's total and an uncited entry are informational lines on stderr. Its word count is the conservative reading: headings, the title block and tables count, references and appendices do not, so a prose-only count runs a few percent lower and a draft near the limit should keep that margin. Two reports judge nothing and serve `review`: `draft <path> --numbers` groups every repeated number and every amount or percentage by value with its heading, line and surrounding words, so a stale participant count sits beside the one that replaced it; `draft <path> --placeholders` lists `TODO`, `TBD` and `[BRACKETED]` placeholders, and with `--placeholder-list "<heading>"` the ones used but not listed there and listed but unused. On the review it reports a pass quoted from a placeholder (`pass-placeholder`), accepts `not confirmed` on the four attested items only, and checks the optional `Checker:` header line, the option set the pass ran, which the next pass reads item 3.1's values from. Every defect line ends `[<rule>; item <ID>]`, naming the checklist item that owns it.

## Commands

Every skill is invoked by name; none is picked up by the model on its own.

| Command                                 | What it does                                                                                                                                                                                                                                                                                                                                      | Writes                                                                                                |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `/experiment-proposal:design`           | Extracts the decisions your material already makes, asks the rest in numbered rounds with a recommendation per question, consults the HCI-researcher subagent on counterbalancing and validity, writes the brief, runs the checker, freezes by commit.                                                                                            | `proposal/design-brief.md`, committed with your OK                                                    |
| `/experiment-proposal:review`           | Confirms the template's mechanics and runs the draft checker, carries an earlier review's waivers and values forward, checks every checklist item (a quoted passage per pass), cross-section consistency, the brief and six substance tests; proposes a fix per failure; applies only the fixes you pick; hands off to the defend stage.          | `proposal/review.md`, and the draft for the fixes picked                                              |
| `/experiment-proposal:lit-search`       | Through one script, keyword-searches Crossref, OpenAlex, arXiv and Semantic Scholar (DBLP on a short query of its own), snowballs one seed at a time through Semantic Scholar, OpenAlex, Crossref and OpenCitations, skips every record already judged, keeps a source only with the claim it supports, stops when a snowball round adds nothing. | `proposal/notes/lit-search-judged.txt`, and a round's records through `--out` under `proposal/notes/` |
| `/experiment-proposal:the-ethics-board` | Rehearses an ethics-committee review of the study: transcript, vulnerability map, revision list.                                                                                                                                                                                                                                                  | `proposal/ethics-review.md` (its review)                                                              |

The order is `design` first, then your draft at the path the brief records (`proposal/draft.md` by default), then `review`; run `lit-search` and `the-ethics-board` whenever the brief's Open items ask for them.

The subagent `hci-researcher` ships with the plugin, restricted to reading; `design` consults it on counterbalancing, control variables, validity threats and confounds. Its description is loaded into every session where the plugin is enabled.

## Agent use

An agent calls a skill by name, as you would: `/experiment-proposal:design material.md`, or the Skill tool with `experiment-proposal:design`. With the argument `agent` (`/experiment-proposal:design agent material.md`; in Codex, where a skill mention carries no arguments, the words "no human will answer" in the message) the skill runs without waiting: `design` marks every unanswered item provisional with `Source: agent run, <date>`, leaves the brief open and ends "brief open, N provisional; the user freezes it with /experiment-proposal:design"; `review` records the four attested items as `not confirmed`, applies no fix and ends "the user picks fixes with /experiment-proposal:review" followed by the hand-off; `lit-search` reports without asking for a seed; `the-ethics-board` proceeds on the inputs given. Nothing an agent run writes is attested or frozen; those steps stay yours.

## Prerequisites

- **git** in your project: `design` freezes the brief by commit.
- **Python 3.11 or later**, as `python3`, for the checker and for `lit-search`'s script; each stops with an install pointer when it is older. `lit-search`'s keys are optional: `OPENALEX_API_KEY` (OpenAlex is skipped without it) and `CONTACT_EMAIL` are read from the environment or from a key file (the file named by `THESIS_PROPOSAL_KEYS`, `api-keys.env` in the working directory, or `~/.config/thesis-proposal/api-keys.env`), `OPENCITATIONS_TOKEN` from the environment only; a Semantic Scholar key is not used, and when that index answers HTTP 429 the script prints `semantic_scholar: skipped (HTTP 429); snowball's graph endpoints cover it` and goes on. Your search terms and seed DOIs go to those public APIs.
- **research-grill** for the defend stage, a separate install this plugin does not declare as a dependency because it is licensed CC BY-NC 4.0: `claude plugin marketplace add scdenney/open-science-skills` then `claude plugin install oss@open-science-skills`. `review` prints these commands ahead of the defend command when it is absent.

## Headless use

The skills run under `claude -p` with `--permission-mode acceptEdits --allowedTools "Read,Write,Edit,Agent,Bash(git:*),Bash(python3:*)"`; pipes and commands outside the allowed prefixes are refused by the permission layer and the skills retry in an allowed form. A `design` run is several turns; use `--continue` for each answer.

## Artifacts and vendored behaviour

`design` writes `proposal/design-brief.md` (the decisions, each with your rationale, what would change it, its status and its source, plus Looked up, Open items and Amendments) and commits it with your OK. `review` writes `proposal/review.md` (one row per checklist item, with the research questions it judged) and edits your draft, wherever the brief's `Draft:` line points, only for the fixes you pick. `lit-search` keeps every judged record, kept or rejected, in `proposal/notes/lit-search-judged.txt`, one line each, and excludes them from later rounds; its output is compact by default and valid YAML. `the-ethics-board`, a vendored skill, writes its review to `proposal/ethics-review.md`; the researcher answers in its transcript are the simulation's, not yours, so check them against what you said. Stop using the plugin and every file stays ordinary Markdown.

## Licences and citations

The plugin is MIT licensed (`LICENSE`). It carries vendored and adapted material from four MIT-licensed sources, listed with their copyright lines in `THIRD-PARTY-NOTICES.md`. Two of those projects ask to be cited: K-Dense-AI/scientific-agents (its README and `CITATION.cff`, read at commit `98c7fae4`) and mohitagw15856/pm-claude-skills (its `CITATION.cff`, read at commit `f93fee74`); their citation files give the preferred forms. The pm-claude-skills repository was unreachable on 2026-10-24, so cite it by name, by commit `f93fee7459e2bf452ec9bc43163004812efba51f` and by its archived revision `swh:1:rev:f93fee7459e2bf452ec9bc43163004812efba51f`.

## Version

The version has one writer, `.claude-plugin/plugin.json`; the brief's `Checklist:` line reads it from there. Each release is tagged `experiment-proposal--v<version>` in the research-vault repository.
