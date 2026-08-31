# Proposed ADR and CONTEXT.md changes

**Date:** 2026-08-31 · **Source:** the [installed asset disposition survey](research/harness-audits/2026-08-30-installed-asset-disposition-survey.md) and [#75](https://github.com/eranroseman/knowledge-harness/issues/75)
**Status:** proposal. Nothing here is adopted.

Second in the series after [2026-08-28](2026-08-28-proposed-adr-and-context-changes.md).

## 1. Scope, and what is deliberately excluded

#75 produced a large body of decisions, and **most of them are not research-vault's.** The ladder, the buckets, the `defer` state, the duplication, fork-obligation and sharing doctrines, the `superpowers` fork, the `eroseman` marketplace and the `sensemaking` name all govern `software-development`. They live on map #53 and in `docs/terminology.md` §4.5, and filing them as research-vault ADRs would repeat an error that recurred through that session: applying one product's authority to another.

What follows is only what bears on **this repository's own contract**.

## 2. Proposed CONTEXT.md additions

### 2.1 `Fork` and `Vendor` are distinct, and the spec currently conflates them

The foundation specification uses the phrase both ways:

- §7:122 — *"`find-sources` … **Vendored** fork of K-Dense `paper-lookup` (MIT)"*
- §7:132 — *"**Vendored forks** coexist harmlessly with installed originals"*

`find-sources` is not a fork. It is a copy taken into this repository at a pin, carrying a provenance header, with no separate distributable and no merge path back to upstream — which is exactly why #24 exists and why the repair is a *re-vendor*, not a merge. The distinction is load-bearing here: it decides whether upstream changes arrive by `git merge` or by someone re-copying, and #97 is about to make that choice for every third-party component this repository carries.

Proposed entries, in CONTEXT.md's existing form, under a new **### Third-party content** heading in `## Language`:

> **Vendor**: To copy third-party content into this repository at a pin, under a provenance header, becoming ours to maintain. Upstream changes arrive only by re-vendoring; nothing merges. The copy must not be hand-edited — the header says so, and `mdformat` breaking that contract is what #24 records.
> _Avoid_: vendored fork, forked in, inlined
>
> **Fork**: To take an upstream repository whole and maintain a patched copy of it as a separate artifact, receiving upstream changes by merge. This repository holds no forks; the term appears here to keep it from being used for vendoring.
> _Avoid_: vendored fork
>
> **Frozen**: Of vendored content, held byte-identical to its pin except for the provenance header, and excluded from formatters. Freezing is what makes the pin meaningful.
> _Avoid_: pinned copy, snapshot

Adopting these implies one correction to the foundation spec: §7:122's *"Vendored fork"* becomes *"Vendored copy"*, and §7:132's *"Vendored forks"* becomes *"Vendored copies"*. Both are amendments in place with a dated note, per that document's own status rule.

### 2.2 These terms will exist in two glossaries, deliberately

`software-development` will need `fork` and `vendor` too — its whole disposition ladder turns on them. Each product defines them in **its own** CONTEXT.md, because #77 ruled there is no shared glossary and no mechanism holding the two aligned; keeping them consistent is a developer responsibility, priced deliberately. The definitions below are written for *this* repository's usage — vendored reference documentation under a frozen contract — and the sibling's will emphasise the distribution side. That they overlap is the expected cost, not a defect to solve.

### 2.3 Not proposed

`rung`, `bucket`, `defer`, `sensemaking` and the sharing check are `software-development`'s vocabulary. §4.5's amendment says each of the three products keeps its own `terminology.md`; that product has no repository yet, so its glossary has nowhere to live and the map's Notes are holding the vocabulary in the meantime. **That gap is worth raising with #58 or #59 rather than filling it here.**

## 3. ADR triage

### 3.1 Candidate for ADR 0006: how research-vault takes third-party content

**Not yet ready — blocked on [#97](https://github.com/eranroseman/knowledge-harness/issues/97)**, which decides the policy. This records that the decision, once made, clears the bar.

Against domain-modeling's three tests:

- **Hard to reverse.** Eleven reference documents are already vendored from `K-Dense-AI/scientific-agent-skills` at pin `336c4f83`, each carrying a provenance header, with `skills/import-source/references/` holding three more of unconfirmed provenance. Changing the policy means re-taking all of them.
- **Surprising without context.** A future reader finds frozen copies of someone else's documentation inside `skills/`, with headers forbidding hand-edits, and no explanation of why they are not simply a dependency.
- **A real trade-off, with the cost already realised.** #24 is the evidence: commit `ce0f1e3` ran `mdformat` across all eleven and silently canonicalised them, violating the frozen-vendor contract. The formatter now excludes those paths. An ADR is the right home for a decision whose failure mode has already happened once.

The decision it would record is not "vendor everything" but the boundary: which classes of third-party content are vendored, which are depended on, and what the frozen contract obliges. #97 separates those classes — copied content, package dependencies, external services — and only the first is in scope.

### 3.2 Below the ADR line

- **The `fork`/`vendor` terminology** — a glossary entry, not a decision. §2.1 above.
- **`sensemaking`, the ladder, the marketplace** — another product's, per §1.
- **The `resolving-merge-conflicts` and `diagnosing-bugs` spine integrations** — design for `software-development`, carried on #60 and #61.

## 4. Noted for `software-development`'s own register, when it has one

Not proposals for this repository — recorded here because the observation came out of #75 and would otherwise be lost when map #53 closes.

### 4.1 The five-rung ladder is that product's first ADR candidate

Against domain-modeling's three tests:

- **Surprising without context — strong.** A reader finds a fork of a 279,648-star repository, thirteen vendored skill directories and eight plugins depended on as-is, and needs to know why three treatments. The organising answer — ownership against upstream flow, with **fork outranking vendor because a fork keeps receiving by merge** — is counterintuitive; vendoring reads as the conservative default until the reasoning is stated.
- **A real trade-off — strong.** Live alternatives, costed: the original adopt-as-is / modify-import / unrelated axis; a four-rung version with no fork rung; and marketplace-entry component selection, which died on Codex's single-path `skills` key.
- **Hard to reverse — partial, and the two halves separate.** The *classification* is cheap to reverse while nothing is built. The **ordering principle** is not: reversing "fork above vendor" means undoing a repository, a marketplace entry and a cutover on both harnesses. The durable commitment is the principle, so that is what an ADR would record.

**Drafted 2026-08-31:** `docs/2026-08-31-proposed-adr-software-development-component-adoption.md` — written out as that product's ADR 0001, recording the ordering principle rather than the per-asset table, per the split above. Held as a proposal because no register exists to accept it; #59 establishing the repository is its trigger.

### 4.2 `Mode` is a term that product's glossary needs

Proposed 2026-08-31 out of #73. This harness has three instances of a **posture set once and persisting across responses** — `caveman` (wired and running), `rethink` (authored, never wired), and superpowers' SessionStart injection — and no glossary distinguishes one from a skill.

> **Mode**: A persistent posture installed by a hook, active across every response until switched off. Distinct from a **skill**, which is invoked on demand and ends when it returns.
> _Avoid_: persistent skill, always-on skill

The distinction earns its place because the two fail differently: **an unwired skill is inert, an unwired mode is invisible.** `eranroseman/rethink` demonstrated exactly that — `hooks/directive.md` authored in full, `plugin.json` declaring `hooks: null`, and nobody noticing because a mode that never activates produces no error. The disposition ladder also treats hooks as one component kind among several, which is right for distribution and wrong for reasoning about failure.

### 4.3 That product has no home for three kinds of record

It is accumulating a **glossary** (`rung`, `bucket`, `defer`, `fork`, `vendor`), **naming rules** of its own under §4.5's each-product-keeps-its-own ruling, and now **architectural decisions**. All three currently sit in map #53's Notes.

**The map's Design doctrine block is functioning as a proto-ADR register** — three entries, each carrying a decision, its reasoning and measured evidence, which is what an ADR is, filed in the only place available. That works as a stopgap and does not survive the map: #58 is written when the frontier empties, at which point the map stops being the live index.

Suggests #59 should establish the register with the repository rather than at build time, and that the ladder is its first entry. Raise with #58 or #59; not this repository's to decide.

**Four kinds of record, now**, counting §4.2's glossary term.

## 5. Follow-up sequence

1. Adopt or decline §2.1's three CONTEXT.md entries.
2. If adopted, amend the foundation specification's two "vendored fork" usages in place with a dated note.
3. Leave ADR 0006 parked until #97 resolves; this document is its trigger record.
4. Raise §4.2 with #58 or #59 — the sibling needs a glossary, naming rules and an ADR register, and the map is holding all three on borrowed time.

## Style reference

CONTEXT.md entries follow the existing form — bold term, one-sentence definition, `_Avoid_:` line. ADRs follow `docs/adr/0005-*`: title, `Status: accepted (date)`, a paragraph stating the decision, then `## Considered Options` with each rejection reasoned.
