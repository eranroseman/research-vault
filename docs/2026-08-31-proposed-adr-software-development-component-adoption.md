# Proposed ADR — `software-development`: how third-party components are taken

**This is a draft for another product's register, held here because that register does not exist yet.**

`docs/adr/` is `research-vault`'s. Filing this there would repeat the error that recurred through #75 — applying one product's authority to another — and `docs/2026-08-31-proposed-adr-and-context-changes.md` §1 rules it out explicitly. §4.1 of that document identifies the ladder as `software-development`'s **first** ADR candidate and §4.3 records that the product has no register to file it in. This draft is what §4.1 describes, written out so that it survives map #53 closing rather than existing only as a note about a candidate.

**Trigger for filing:** #59 establishes the repository and its register. Until then this is a proposal, unaccepted, and nothing depends on it.

**Numbering:** this is that product's ADR **0001**, not a number in `docs/adr/`. `0005` there is spent (`0005-better-bibtex-owns-the-bibliography-export.md`, landed via #93) and `0006` is parked pending #97.

---

# Third-party components are taken at the highest rung that still works

Status: **proposed** (2026-08-31, from #75) — no register exists to accept it

**`software-development` takes third-party content at one of five rungs — plugin as-is, fork plugin, vendor component, adapt component, write — ordered by how much ownership the treatment transfers to us against how much upstream still flows in. The rung is chosen by descending until one works, never by preference, and the ordering places _fork above vendor_ because a fork keeps receiving upstream by merge where a vendored copy stops receiving anything.** Buckets — the `required` / `recommended` distinction — exist on rungs 1 and 2 only, because a component we adapt or write has no upstream to be recommended *from*. A `defer` verdict is only a verdict if it carries a trigger.

The ordering is the decision. The five names are how it is applied.

## Considered Options

**The original axis: adopt-as-is / modify-import / unrelated.** This is what #75 was written against and it failed on first contact with real assets. It has no term for a fork, so `superpowers` — which cannot be taken as-is and must not be vendored — had nowhere to sit. It also conflates *what we do to a thing* with *whether we want it*: "unrelated" is a scope judgement, while the other two are treatments, so the axis cannot answer "we want it and none of these fit."

**A four-rung version with no fork rung.** Simpler, and wrong for a specific measured reason. `superpowers` carries **26 qualified `superpowers:` cross-references across 9 files**, none of them inside `skills/brainstorming/`. Vendoring the components breaks all 26 the moment they leave the namespace; forking preserves the namespace and costs a 10-file patch against two trivial merge conflicts. Without a fork rung the only expressible answers were "take everything including the skill we must remove" or "take the pieces and break every internal reference."

**Marketplace-entry component selection** — declaring which components of a plugin to install, rather than treating the plugin as atomic. Died on a platform fact: Codex's manifest has a single `"skills": "./skills/"` path with no per-component selection, so a treatment expressible on Claude Code would have no Codex equivalent. Rejected because the two harnesses must reach the same outcome, not merely both be served.

## Consequences

**A fork is an obligation, not a copy.** Rung 2 buys continued upstream flow and pays for it with merge duty: #63 must watch the fork's merge-base against upstream HEAD, and must catch **unqualified** references — upstream has already added `skill_view("brainstorming")`, which a `grep superpowers:brainstorming` misses and which auto-merges clean. A fork nobody merges silently becomes a vendored copy with extra steps.

**The ordering is expensive to reverse; the classification is cheap.** While nothing is built, moving an asset between rungs costs an edit. Reversing "fork above vendor" costs a repository, a marketplace entry and a cutover on both harnesses. That asymmetry is why this ADR records the principle and treats the per-asset table as data.

**`defer` without a trigger silently becomes rejection.** Four skills parked in the standing recommendations register printed as `not-adopted` in four separate survey passes, because the axis then in use had no defer state and a parked skill was indistinguishable from a declined one. The trigger requirement exists to make that failure impossible rather than unlikely.

**Rungs 3–5 leave the bucket vocabulary behind, deliberately.** Asking whether an adapted component is "recommended" is a category error — there is no upstream artifact for a user to install instead. This is why bucket questions (#96) depend on roster decisions that could still land at rungs 1–2, and are unaffected by ones that cannot.

## Not in this decision

**Which product a component belongs to** — `sensemaking` or `software-development` — is a separate question with its own test: do the component's file paths and terminal state resolve in both products, and is a reference to another skill binding or merely a mention. That test earned itself when six verdicts changed under challenge, all having reasoned from a skill's description rather than from what it operates on and exits into. It is a sibling ADR candidate, and conflating it with this one would repeat in miniature the error the original three-way axis made: mixing *how we take a thing* with *where it goes*.
