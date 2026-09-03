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

**Source 4's queries were added mid-search, and S19 v2 now requires that to be declared.** The first three ran, returned empty, and three more were written in response. That is adaptive stopping, not saturation, and the first write-up recorded the six terms without recording that three were additions. Declared here retrospectively; a compliant run would have declared the plan before starting.

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

**S16 is the flaw in every case: none produces a coverage map, because none takes a requirement set as input.** *Recorded on 2026-09-03 against S1, which then read "consumes a requirement set that has been approved". S1 was rewritten the same day to test the set's screenability rather than its approval, so the ground moves to S16 — also a floor, and the cleaner statement of what these candidates lack.* Two near-misses of the word rather than the thing — `skill-judge`'s "requirements" are SKILL.md *format* rules, and `dependency-updater`'s are `requirements.txt` files.

**Three were wrongly eliminated on S5 in the first write-up, and that is withdrawn.** `vendor-review` produces *"a 2-3 sentence recommendation"*, `skill-judge` scores with *"instant score ≤5"* red flags, and `claude-automation-recommender` recommends. On the author's ruling of 2026-09-03 none of that violates S5: a per-candidate opinion is evidence the decider weighs, not a decision, and S23 already records signal *direction* on the same principle. S5 forbids **closing** the decision — naming one answer — which none of these does to a requirement set, because none has one to close over. **S16 is the sole ground for every elimination here.**

**Excess capability (S22):** `vendor-review` carries a total-cost-of-ownership model, negotiation points and a renewal path; `dependency-updater` carries auto-patching. None is asked for, and for one developer each is surface area to read and keep straight, so the excess costs.

**Near-miss (S21):** none. Every gap is categorical, not marginal — there is no restatement of any requirement under which one of these would qualify.

## Inherited requirements for `writing-specs`

Five requirements retired from the sourcing set on 2026-09-03 because they are screening rules, and screening is the design phase's work. Offered to `writing-specs` rather than written into it: that skill has no requirement set, and inventing one for it would be the failure this project is still marked for.

- **Eliminate a candidate only for a named critical flaw, never for incomplete coverage.** *"An alternative should not be considered 'non-viable' because it fails to close 100 percent of the shortfall"* — AoA Handbook §9.1.1. This is the rule whose absence produced this project's failed screen, and it is worth more downstream than it was here.
- **Name which requirements form the screen before screening, and screen on those alone.** Every COTS method surveyed does this; the screen may be narrower than the must-haves and never wider.
- **Bound the candidates examined by what can be evaluated, not by fit.** Where more survive than the bound allows, narrow the screen rather than selecting among survivors — ranking them requires a comparison the sourcing phase is forbidden to make.
- **Record a candidate that narrowly missed, or that would qualify under a requirement stated differently, and return it rather than dropping it.** FAA NAS SEM §4.6.3.5; FAR 10.001(a)(3)(ii)(C) with 10.002(c)'s return path.
- **Route a weak health signal to a treatment rather than to rejection.** Low maintenance argues for *copy frozen* over *install as-is and keep merging*. Marked a hypothesis when written and still one: the thresholds are published, the routing is not.

**Take them or decline them.** The evidence for each is in the sourcing set's history and in `docs/research/`.

## What the run found about the requirements

The screen ran this time, and produced one finding worth more than the verdict.

**All nine were eliminated on a single floor, and the other five screened nothing.** S1, S3, S5, S8 and S15 never got to act — and S5's apparent three eliminations were my misreading, withdrawn above, which makes the concentration total rather than near-total. That is not the total-coverage failure returning — S1 is a categorical property, not a coverage count, and a screen that eliminates on *"does not take a requirement set"* is eliminating on the right kind of thing. But it means **the screen added no information the search had not already produced.**

The cause is a duplication between two requirements written a day apart. **S24's candidate concept** — *"takes a set of requirements and reports which existing components cover them"* — and **S1's floor** are the same test, applied at the search stage and again at the screen. Anything the concept admits, S16 admits; anything the concept excludes never reaches the screen. The nine candidates only reached the screen because the search filter was keyword-based and looser than its own stated concept.

That is worth a decision rather than a fix here: either the search concept should be enforced as the search runs, in which case the screen inherits fewer candidates and S16 becomes inert, or the concept should be deliberately loose and S16 kept as the real gate. **The current arrangement does both and gets no discrimination from either.**

**Two requirements were exercised for the first time and held.** S8's two-step worked as intended — descriptions carried nine candidates into the search cheaply, and four bodies that had been skipped were read before any finding was made. S13's timing worked: licences were gathered at screen entry, not at discovery, and two remain unread because their marketplace was not fetched, recorded rather than guessed.
