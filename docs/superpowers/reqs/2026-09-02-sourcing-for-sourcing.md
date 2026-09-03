# Sourcing findings: the `sourcing` skill

> **What this is.** A sourcing run for the `sourcing` skill itself, done by hand against all 23 requirements in `docs/superpowers/reqs/2026-09-02-sourcing.md`. It answers that document's open question — *"Does this skill screen its own candidates?"* — by trying it.
>
> **What consumes it.** `writing-specs`, together with the requirement set, per S14. Nothing here is a decision: no verdict adopts, adapts or rejects anything (S5, S6).
>
> **No build decision is made here, and none is due.** The author's ruling of 2026-09-03: the build decision comes after sourcing is done, and sourcing is not done. S6 would in any case place it downstream, with `writing-specs` — which does not exist yet either.
>
> **Incomplete, and blocked for a stated reason.** The search ran to saturation. **The screen did not run at all**, because S17 draws it from the hard floors the requirement set marks and the sourcing set has no `*Floor:*` fields. See "Why the screen did not run".

## The search (S19, S20)

**Budget, declared before searching** (S20): five sources, stopping when a new source returns only candidates already seen. No time limit was set and none was reached. **The short candidate list below is a fact about the field, not a limit of the search** — that distinction is the whole reason S20 exists.

**Sources, in order, with what each added** (S19):

| #   | Source                                                                                                                       | New candidates                                        |
| --- | ---------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| 1   | Installed skills, `~/.claude/skills`                                                                                         | `skill-judge`                                         |
| 2   | Installed plugin skills, all marketplaces on disk                                                                            | `claude-automation-recommender`, `dependency-updater` |
| 3   | `obra/superpowers`, `anthropics/skills`, `anthropics/knowledge-work-plugins`, `mattpocock/skills`, `addyosmani/agent-skills` | `vendor-review`, `vendor-check`, `source-management`  |
| 4   | GitHub repository search, three query forms                                                                                  | none                                                  |
| 5   | `duthaho/claudekit`, `softaworks/agent-toolkit`, `product-on-purpose/pm-skills`, `tonone-ai/tonone`                          | `keel-vendor`, `score-compare`, `bench-compare`       |

**Saturation reached at source 5**: its returns are the same two kinds already seen — vendor-relationship management, and statistical comparison of models or benchmarks. Neither is new in kind.

## Candidates found

Read at each repository's HEAD on 2026-09-02.

| Candidate                        | Supplier / originator (S13)                     | Body read? (S8)           |
| -------------------------------- | ----------------------------------------------- | ------------------------- |
| `vendor-review`                  | Anthropic — `anthropics/knowledge-work-plugins` | **Yes**, 104 lines        |
| `vendor-check`                   | Anthropic — same repository                     | Yes, 159 lines            |
| `source-management`              | Anthropic — same repository                     | Yes, 173 lines            |
| `keel-vendor`                    | `tonone-ai/tonone`                              | **No — description only** |
| `skill-judge`                    | installed plugin, originator not established    | **No — description only** |
| `claude-automation-recommender`  | installed plugin, originator not established    | **No — description only** |
| `dependency-updater`             | installed plugin, originator not established    | **No — description only** |
| `score-compare`, `bench-compare` | `tonone-ai/tonone`                              | **No — description only** |

**Four of nine were found from a description and never read.** Under S8's two-step that is legitimate for discovery and disqualifying for judgement, so they are **not-examined under S18** — a statement about this run's budget — rather than **undetermined under S16**, which would be a claim about their coverage. My first write-up used the wrong label. Licences and IP rights (S13) were not read for any candidate, because the screen they would feed did not run.

## What each covers (S16)

Three states: covers, does not cover, **could not be determined**. Candidates never read are not in these states at all — they are not-examined under S18. Absent an affirmative completeness claim, read this table as incomplete.

| Candidate           | Consumes a requirement set (S1) | Findings not decisions (S5, S6) | Component-level (S4) | Coverage map (S16) |
| ------------------- | ------------------------------- | ------------------------------- | -------------------- | ------------------ |
| `vendor-review`     | does not cover                  | does not cover                  | does not cover       | does not cover     |
| `vendor-check`      | does not cover                  | does not cover                  | does not cover       | does not cover     |
| `source-management` | does not cover                  | does not cover                  | does not cover       | does not cover     |
| all others          | undetermined                    | undetermined                    | undetermined         | undetermined       |

`vendor-review` is the closest of the three read in full, and its shape is the reason it is far: it produces *"a 2-3 sentence recommendation"* and evaluates on **cost of ownership, vendor financial stability, SLA compliance and contract lock-in**. Those are properties of a commercial relationship. The candidates this skill screens are MIT-licensed markdown files with no vendor, no contract and no SLA.

**Excess capability (S22):** `vendor-review` carries a TCO model, a negotiation-points section and a renewal-decision path — none of which this need asks for. For one developer that is surface area to read and keep straight, so the excess costs rather than helps.

**Near-miss (S21):** none. No candidate missed by a margin worth recording; the gap is categorical rather than narrow.

## Why the screen did not run

S17: *"the artifact lists the screening requirements and why each was chosen… The only choice made here is which floors enter the screen"*, drawn from the hard floors the requirement set marks under `writing-reqs` R43.

**The sourcing requirement set has no `*Floor:*` fields.** It is not a `writing-reqs` output, so nothing marked any. Without them S17 has nothing to draw from, and S15 — which eliminates only on a named critical flaw, defined as failing a hard floor — has nothing to test against.

So **no candidate is eliminated here**, and none should be read as rejected. That is S15 working: a candidate that covers little is recorded as covering little, not excluded.

**What unblocks it:** the author marks floors across the 23. S17 was generalised on 2026-09-03 — it now reads whatever floors a set marks, whatever produced that set, and where a set marks none it says so and screens on nothing. That makes this run's blocked state expressible, but it does not fill it.

## What this run found about the requirements themselves

Doing it by hand was the point, and three requirements broke on contact.

- ~~**S17 and S15 are unrunnable against any set that is not a `writing-reqs` output.**~~ **Fixed 2026-09-03.** Both reached for R43's marks by name. The author's ruling: this skill cares about the *form* of a requirement set, never about what produced it. S17 now reads whatever floors a set marks and can report a set that marks none.
- ~~**S8 has no partial state.**~~ **Not a defect; I misapplied it.** S8 now carries the two-step it always implied and that skills themselves use: a description may narrow the *search*, only a body may ground a *finding*. Discovery stays cheap. The four unread candidates were never undetermined — they were not-examined, which S18 already provided for.
- ~~**S13 could not be attempted.**~~ **Fixed 2026-09-03:** due when a candidate enters the screen, not when it is found.
