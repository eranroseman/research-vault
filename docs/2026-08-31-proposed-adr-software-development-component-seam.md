# Proposed ADR — `software-development` / `sensemaking`: which product holds a component

**A draft for another product's register, held here because that register does not exist yet.**

Same standing as [the component-adoption ladder draft](2026-08-31-proposed-adr-software-development-component-adoption.md): `docs/adr/` is `research-vault`'s, and `docs/2026-08-31-proposed-adr-and-context-changes.md` §1 rules out filing another product's decisions there. This is `software-development`'s **ADR 0002**, sibling to that one and deliberately separate from it — conflating *how a component is taken* with *where it goes* is the error the original adopt-as-is / modify-import / unrelated axis made.

**Trigger for filing:** #59 establishes the repository and its register.

---

# A component is shared only if its plumbing resolves in both products

Status: **proposed** (2026-08-31, from #72, #73 and #75) — no register exists to accept it

**A component belongs in `sensemaking` — the distributable both products install — only if its file paths and its terminal state resolve in both products. The judgement is made by reading the component's body, never its description; and within the body, a binding call is distinguished from a mention. Everything else belongs to the product that can actually run it.** Where a component is a template consumed at build time rather than a capability either product ships, the axis does not apply at all.

The test is deliberately mechanical — a rule that can be run rather than remembered.

## Considered Options

**Allocate by capability — what the component is *for*.** The obvious reading, tried twice on `consistency-audit` and reversed both times. One pass placed it in `software-development` on framing vocabulary (*"read a **repository** whole"*); the next reversed it to `sensemaking` on capability, since *"contradictions, duplication, drifted terms, stale claims"* is exactly what a research vault accumulates. Both were reasoning from the description, and reading the body settles it against both: the report destination is hardcoded to `docs/superpowers/specs/` — a path no vault has — and the terminal state is *"Invoke writing-plans skill"*, which does not exist on a vault install.

**Six verdicts changed under challenge during #75, all making this same error.** That is the evidence this ADR rests on, and it is why the rule names plumbing rather than purpose.

**Allocate by the caller graph.** Attractive, and it argues the *opposite way* on the case that motivated it. Three skills call `domain-modeling`: `wayfinder` (`sensemaking`), `triage` and `improve-codebase-architecture` (both `software-development`) — two of three favouring `software-development`, which is where the body already pointed. But #73 showed the input is unreliable: banked analysis read `codebase-design`, `writing-plans` and `brainstorming` as a call graph resolving inside one product, when the first is invoked *"if available"* and the other two are prose pointers. Mentions had been counted as dependencies. The caller graph is admissible evidence only after binding calls are separated from mentions — which is the body-reading the rule already requires, so it adds nothing the rule does not.

**Ship everything to both products.** Rejected on measured damage, not tidiness. `domain-modeling` writes `CONTEXT.md` and `docs/adr/` and **creates them where absent**, so a vault install does not merely carry an unused skill — it acquires a repository's scaffolding. It also fails the duplication doctrine independently: two model-invocable skills of the same purpose cannot coexist, and no lever on either harness resolves the collision (`skillOverrides` returns `"on"` unconditionally for plugin-sourced skills at Claude Code 2.1.220, `/plugin` toggles whole plugins only, and Codex has no skill-level lever at all).

## Consequences

**A dangling call is a correct outcome, not a defect.** `wayfinder` ships in `sensemaking` and calls `domain-modeling`, which does not. On a vault-only install that call finds nothing — and that is the right result, because the alternative is shipping the scaffolding damage above. A shared skill may reference a component the other product lacks, provided the reference is not load-bearing.

**A component needing a different exit per product is two components, not one shared one.** `consistency-audit`'s method transfers to a vault; its plumbing does not, and a vault already has a destination for adjudicated findings — `inbox/review-queue.md`, append-only, carrying reason codes and human acknowledgment. The honest answer there is a vault-side derivative sharing the method, not one skill with a conditional exit. Recorded for #79.

**Sharing is the exception, and the test is restrictive by construction.** Of the six verdicts #75 owed, exactly one came out shared. That ratio is the rule working, not evidence it is miscalibrated.

**The axis assigns need, not file location.** `superpowers` is `software-development`'s, meaning that product depends on it and `research-vault` does not. The fork remains a separate plugin with its own root; nothing moves into anyone's tree.

**It only ever asks about skills.** #77 settled that `sensemaking` holds skills and nothing else — no shared glossary, no shared naming authority, each repository keeping its own `CONTEXT.md` and `terminology.md`, with alignment a developer responsibility priced deliberately as a mechanism that would be overkill. So this rule is never asked about vocabulary or decisions, only about components.

## What this does not decide

**How a component is taken** — the five-rung ladder — is ADR 0001. A component can sit at any rung and be allocated by this rule independently; the two questions are orthogonal, and `rethink-audit` demonstrates it, landing at rung 4 in `sensemaking` while `consistency-audit` sits in `software-development`. Same family, opposite answer, and it is the plumbing check rather than the family resemblance that separates them.
