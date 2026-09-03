# Sourcing findings: the `sourcing` skill

> **What this is.** A sourcing run for the `sourcing` skill itself, against all 24 requirements in `docs/superpowers/reqs/2026-09-02-sourcing.md`. Run by hand on 2026-09-02, blocked at the screen, and **completed 2026-09-03** once the requirement set was marked screenable.
>
> **What consumes it.** `writing-specs`, with the requirement set, per S14. Nothing here decides: no finding adopts, adapts or rejects (S5, S6).
>
> **Result: no candidate qualified.** Nine found, all nine eliminated on one named floor. The decision that follows is not made here.

## The search (S19, S20, S24)

**What a candidate had to be** (S24): a skill, plugin or documented method that takes a set of requirements and reports which existing components cover them — the build-or-buy screen itself, not a tool for evaluating a single candidate on its own merits.

**Budget, declared before searching** (S20): five sources, stopping when a new source returns only candidates already seen. No time limit was set and none was reached. **The short list below is a fact about the field, not a limit of the search.**

| #   | Source                                                                                                                       | Terms used                                                                                                                                                                                                         | New candidates                                        |
| --- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------- |
| 1   | `~/.claude/skills`                                                                                                           | full listing, read                                                                                                                                                                                                 | `skill-judge`                                         |
| 2   | Installed plugin skills, all marketplaces on disk                                                                            | full listing, read                                                                                                                                                                                                 | `claude-automation-recommender`, `dependency-updater` |
| 3   | `obra/superpowers`, `anthropics/skills`, `anthropics/knowledge-work-plugins`, `mattpocock/skills`, `addyosmani/agent-skills` | tree listing filtered on `sourc\|select\|evaluat\|adopt\|vendor\|depend\|compar\|choos\|screen\|shortlist`                                                                                                         | `vendor-review`, `vendor-check`, `source-management`  |
| 4   | GitHub repository search                                                                                                     | `agent skill evaluate dependency adopt`; `claude skill build-or-buy`; `skill vendor selection COTS`; `agent-skills evaluate options`; `skill compare alternatives decision`; `claude skill procurement evaluation` | none                                                  |
| 5   | `duthaho/claudekit`, `softaworks/agent-toolkit`, `product-on-purpose/pm-skills`, `tonone-ai/tonone`                          | same filter as source 3                                                                                                                                                                                            | `keel-vendor`, `score-compare`, `bench-compare`       |

**The source-4 null was tested, not assumed** (S24). All six queries returned empty, which is a suspicious result for a search engine rather than a fact about the field, so `gh search repos "claude code skills"` was run as a control and returned three repositories. The tool worked; the field is empty of this.

**Saturation at source 5**: its returns are the two kinds already seen — vendor-relationship management, and statistical comparison of models or benchmarks. Nothing new in kind.

## The screen (S15, S17)

**Screening requirements, named before any candidate was judged** (S17), drawn from the set's six hard floors: **S1** (consumes an approved requirement set), **S3** (findings in its own artifact), **S5** (evidence, not choice), **S8** (judges the body), **S15** (eliminates only on a named flaw), **S16** (coverage map).

Every candidate's body was read (S8). Findings quote the body, not the description.

| Candidate                       | Supplier / licence (S13)                    | S1    | S5    | Eliminated on |
| ------------------------------- | ------------------------------------------- | ----- | ----- | ------------- |
| `vendor-review`                 | Anthropic · Apache-2.0                      | fails | fails | **S1, S5**    |
| `vendor-check`                  | Anthropic · Apache-2.0                      | fails | —     | **S1**        |
| `source-management`             | Anthropic · Apache-2.0                      | fails | —     | **S1**        |
| `keel-vendor`                   | tonone-ai · MIT                             | fails | —     | **S1**        |
| `score-compare`                 | tonone-ai · MIT                             | fails | —     | **S1**        |
| `bench-compare`                 | tonone-ai · MIT                             | fails | —     | **S1**        |
| `skill-judge`                   | softaworks/agent-toolkit · licence not read | fails | fails | **S1, S5**    |
| `dependency-updater`            | softaworks/agent-toolkit · licence not read | fails | —     | **S1**        |
| `claude-automation-recommender` | Anthropic · `claude-code-setup`             | fails | fails | **S1, S5**    |

**S1 is the flaw in every case: none takes a requirement set as input.** Two near-misses of the word rather than the thing — `skill-judge`'s "requirements" are SKILL.md *format* rules, and `dependency-updater`'s are `requirements.txt` files.

**S5 additionally fails three.** `vendor-review` produces *"a 2-3 sentence recommendation"*; `skill-judge` scores on tables with *"instant score ≤5"* red flags; `claude-automation-recommender` recommends, thirty-five times over. Each decides where this skill is required to gather.

**Excess capability (S22):** `vendor-review` carries a total-cost-of-ownership model, negotiation points and a renewal path; `dependency-updater` carries auto-patching. None is asked for, and for one developer each is surface area to read and keep straight, so the excess costs.

**Near-miss (S21):** none. Every gap is categorical, not marginal — there is no restatement of any requirement under which one of these would qualify.

## What the run found about the requirements

The screen ran this time, and produced one finding worth more than the verdict.

**All nine were eliminated on a single floor, and the other five screened nothing.** S3, S8, S15 and S16 never got to act. That is not the total-coverage failure returning — S1 is a categorical property, not a coverage count, and a screen that eliminates on *"does not take a requirement set"* is eliminating on the right kind of thing. But it means **the screen added no information the search had not already produced.**

The cause is a duplication between two requirements written a day apart. **S24's candidate concept** — *"takes a set of requirements and reports which existing components cover them"* — and **S1's floor** are the same test, applied at the search stage and again at the screen. Anything the concept admits, S1 admits; anything the concept excludes never reaches S1. The nine candidates only reached the screen because the search filter was keyword-based and looser than its own stated concept.

That is worth a decision rather than a fix here: either the search concept should be enforced as the search runs, in which case the screen inherits fewer candidates and S1 becomes inert, or the concept should be deliberately loose and S1 kept as the real gate. **The current arrangement does both and gets no discrimination from either.**

**Two requirements were exercised for the first time and held.** S8's two-step worked as intended — descriptions carried nine candidates into the search cheaply, and four bodies that had been skipped were read before any finding was made. S13's timing worked: licences were gathered at screen entry, not at discovery, and two remain unread because their marketplace was not fetched, recorded rather than guessed.
