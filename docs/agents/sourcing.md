# Sourcing

A **sourcing screen** is how a component gets chosen: a bounded question, a screened candidate set, recorded exclusions, **the exit**, and a handoff. That definition lives here.

**The exit** is what remains if the component goes away — one line, on every verdict including `adopt`. It is not a rule and carries no linter; it is part of what a screen *is*, because a screen that never asked it has not finished. Adoption is where it bites hardest: a `build` is ours to delete, while an adopted component can leave artifacts nobody can read without it. The good answer is usually short — stop invoking it and what it wrote is ordinary vault content — and an answer that cannot be written in a line is the finding.

This file carries one rule.

## The build bar

**When it applies:** at the moment a sourcing screen records a `build` or `adapt` verdict for a component. Not while screening, not afterwards — the verdict is what triggers it, and a screen that reaches no such verdict never meets this rule.

**What it requires:** the verdict names the numbered *must* that no candidate met, and points at the screen that recorded the candidates. In the component register those are the `floor_failed` and `decided_in` columns, and the register's linter rejects a `build` or `adapt` row at the high bar whose `floor_failed` is empty or does not resolve to a numbered must inside its `decided_in`.

**Which tier a component is in, the screen decides and records.** The register does not carry it: a register row holds facts and pointers, and the tier is part of the reasoning (assembly spec, decisions 14 and 18). So a screen concluding `build` or `adapt` names the tier it judged the component to be in, and the linter reads it through the row's `decided_in`.

**Where the bar is high:**

| Tier               | Examples                              | Bar for `build` or `adapt`         |
| ------------------ | ------------------------------------- | ---------------------------------- |
| **Prompt-bearing** | skills, agents, a compile engine      | **high** — `floor_failed` required |
| **Mature tool**    | Better BibTeX, Zotero plugins, ZotLit | **high** — same                    |
| **Glue**           | a doctor probe, a tag map, a lint     | **low** — one line of reason       |

`adopt`, `gap`, `reject` and `open` carry no constraint at any tier.

`adapt` carries the same constraint as `build` at the high bar. Without that, a lane that wants to build without screening writes `adapt` instead — and in this repository the evasion is already available, because `research_vault/zotero.py` exists to adapt.

**Capture is a mature tool, not glue**, and saying so is the point of the tiers. Its candidates carry years of edge-case handling this repository has already hit. A Python connector reads as "a doctor probe, a tag map, a lint" if nobody names its tier, and glue owes only one line of reason — which would exempt the exact decision the rule was written for.

## Why the bar exists

The adopt→build gap is not uniform, and adopt-first is not dogma. Writing and maintaining a skill is an art, and an adopted one keeps improving without us. A mature tool carries edge cases we have not hit yet. A glue script carries almost nothing, and adopting one imposes a pin, a drift check, an upgrade path and a licence review that can cost more than the code. The tiers are that counterweight, stated up front rather than discovered later.

The rule exists because a prior belief of this repository — that writing our own Zotero connector is simpler and better than adopting one — may well be correct and cannot be evaluated, because no screening record was kept.

**It does not forbid building. It makes a build verdict falsifiable.**

## The higher rung

The rung above this rule is the discipline living in the `software-development` brainstorming skill, so that no repository needs to carry it. **It is not filed — no such issue exists as of 2026-09-06** (checked). Filing it upstream is the right move and this repository cannot wait on it either way, since that is a separate project on its own schedule.
