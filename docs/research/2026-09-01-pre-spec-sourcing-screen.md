# Sourcing screen: twelve candidates against twenty-nine musts

Disposition: historical (2026-09-06) [should-be-scoping-review]

Research note, 2026-09-01. Evidence for the sourcing decisions in `docs/superpowers/reqs/2026-09-01-writing-reqs.md`.

**Question asked:** is there anything we can use to fulfil these requirements? Pass/fail per requirement, no partial. A candidate failing any must is out, not weaker.

**Method.** One isolated agent per candidate. Each was given the twenty-nine requirements and its own candidate only — it did not know what else was being screened, could not compare, and was instructed not to rank or recommend. Every screen was then re-run by an adversarial verifier instructed to refute the passes, defaulting to refuted where the deciding line could not be confirmed. Judgement was from the artifact body — SKILL.md, templates, references — never from a description or README.

______________________________________________________________________

## Result

| Candidate                                         | Licence    | Claimed passes                       | Fails |
| ------------------------------------------------- | ---------- | ------------------------------------ | ----- |
| `write-spec` — anthropics/knowledge-work-plugins  | Apache-2.0 | R1, R7, R14, R17, R20, R21, R22, R25 | 21    |
| `interview-me` — addyosmani/agent-skills          | MIT        | R1, R7, R10, R20, R21, R22, R24      | 22    |
| `shape-spec` — duthaho/claudekit                  | MIT        | R1, R2, R21, R22, R24, R25           | 23    |
| `requirements-clarity` — softaworks/agent-toolkit | MIT        | R1, R2, R20, R21, R22                | 24    |
| `deliver-prd` — product-on-purpose/pm-skills      | Apache-2.0 | R7, R20, R21, R22, R25               | 24    |
| spec-kit `/specify` — github/spec-kit             | MIT        | R1, R5, R15, R20, R24                | 24    |
| `alirezarezvani`'s PRD                            | MIT        | R1, R20, R21, R22, R25               | 24    |
| `define-problem-statement` — product-on-purpose   | Apache-2.0 | R1, R7, R20, R22, R25                | 24    |
| `helm-brief` — tonone-ai/tonone                   | MIT        | R1, R20, R21, R25                    | 25    |
| `brainstorming` — obra/superpowers                | MIT        | R1, R5, R7, R10                      | 25    |
| `create-prd` — phuryn/pm-skills                   | MIT        | R1, R20, R22                         | 26    |
| `framing-doc` — rjs/shaping-skills                | **none**   | R11, R13, R24                        | 26    |

**Every verification refuted something.** Surviving pass sets after adversarial re-check ran between one and three requirements. **Nothing exceeds three of twenty-nine.**

______________________________________________________________________

## What follows

**Rungs 1, 2 and 3 are closed by measurement.** Installing, forking or copying any of these means taking something that fails twenty-six musts. That is not a marginal call.

**The decision is between copy-plus-delta on a chosen skeleton, and authoring to credited designs** — and since the patterns come from six sources, mostly the latter.

______________________________________________________________________

## Findings that changed a sourcing decision

**`write-spec` is the only candidate passing R14 after verification.** Its body: *"Requirements: Categorized as Must-Have (P0), Nice-to-Have (P1), and Future Considerations (P2), **each with acceptance criteria**"* and *"For each requirement… Include acceptance criteria."* A per-requirement fit criterion, which nothing else has.

An earlier pass in this session had rejected it for *"no per-requirement fit criterion"* — wrong, about a file that had been read. Correcting that verdict does not make it a source to copy from: re-reading the body on 2026-09-01, every line of its acceptance-criteria section is already held here from a higher rung — 29148 5.2.5 and 5.2.7, 12207, Volere, and BDD for Given/When/Then, which write-spec relays rather than originates. Its own contribution is the P0/P1/P2 three-tier scheme, which this set declines. **The pass is kept as a measurement; no text is taken.**

**`interview-me` fails the loop it was chosen for.** Measured failures:

- **R4** — *"Wait for the user to react before asking the next question"*, with the red flag *"Three or more questions in a single message: that's batching, not interviewing."* Independent questions each cost a round-trip by mandate.
- **R5** — a single guess is the mandated format, and alternatives are argued against explicitly: *"Listing options widens the search; asking narrows it."*
- **R8** — nothing is written until the end: *"When your confidence is high, write back what you now think the user wants."* There is no running record to append to.
- **R9** — per-requirement confirmation is impossible, because requirements are never written individually.

Its loop is **intent-confirmation written once at the end**; ours is write-as-you-go. What survives is R10's gate — *"The gate is an explicit 'yes'"*, with *"Silence isn't confirmation"* and the enumerated false yeses — and R7, and the confidence-number-with-a-reason as an honesty device.

**`framing-doc` passes R11 and R13 and nothing else** — exactly the provenance pair, which is what it was taken for. It has **no LICENSE file**, so it is an idea source regardless.

**`brainstorming` claims four.** Expected and not disturbing: the screen measures artifact content, and the skeleton is being taken for its structure — classifier, gate, checklist, review ritual — not its content.

**Two caveats on that number, both real.** Four is a *claimed* set; **which of the four survived verification is recorded nowhere**, here or upstream, so it does not contradict the "nothing exceeds three" headline but neither does it corroborate it. And one of the four is R10 — so the claim that `interview-me` offered *"the only termination condition that is neither a score nor a count"* was unsupported. **Dropped 2026-09-01**, and it was wrong on its own terms besides: `interview-me`'s headline stop is *"The 95% Confidence Stop"*, a self-judged score. What it uniquely supplies is Step 5's enumeration of non-agreement, not a termination condition.

______________________________________________________________________

## What each requirement discriminated

Recorded here so the requirement set does not have to carry screening arithmetic.

- **R24** screened. Four of twelve candidates claimed it — `interview-me`, `shape-spec`, spec-kit `/specify`, `framing-doc` — and eight failed. Verification then refuted at least one of the four, `framing-doc`, which survives on R11 and R13 only. An earlier note in the requirements document claimed R24 screened nothing, which was false against this table.
- **R7** drove no rejection except jointly with R1.
- **R29** was failed by every candidate, so it discriminated nothing — the same shape as R26–R28 below. An obligation on what gets built, not a filter on what might be taken.

______________________________________________________________________

## A limit of the screen

Every candidate failed **R26, R27 and R28** — the prior-art, competitive-analysis and sourcing steps. No skill in any roster contains three sub-steps that are themselves skills.

That is a measurement of **granularity**, not of the field. Those three are pipeline requirements, and a pipeline is composed rather than sourced. Screening single skills against them guarantees a universal fail that carries no information.

Recorded as an open question against the requirement set rather than treated as a finding about the candidates.

______________________________________________________________________

## Provenance

Screened at whatever each repository's HEAD was on 2026-09-01. **One provenance failure found, and it undercuts this claim.** The spec-kit `/specify` rejection cited a hard error on empty input and a three-marker clarification cap; re-reading `presets/lean/commands/speckit.specify.md` and `presets/scaffold/commands/speckit.specify.md` the same day found neither — both are 23 lines, and `NEEDS CLARIFICATION` is uncapped in `templates/spec-template.md`. So at least one screen read something other than the HEAD recorded here: a stale cache, a different preset, or an older version. Treat the date as the intent of the method, not as verified for every row. Licences were read from LICENSE files, not from GitHub's detected label. `framing-doc` has no LICENSE file — verified, not inferred.

Candidates surfaced but not screened, from an earlier sweep and carried forward as idea sources only: `matter-intake-scoping` (lawve-ai), `incoming-request-advisor` and `prd-development` (deanpeters, CC BY-NC-SA), `quality-playbook` and `doc-and-modernize` (github/awesome-copilot), `neuroarxiv` and `adhd` (UditAkhourii).
