# Rethink audit: the zero-runtime-dependency constraint

Date: 2026-08-20. Method: `/rethink` (fresh-question pass of the rethink-audit rungs). Subject: the "core carries zero runtime dependencies" policy enshrined in spec §8 earlier the same day. Outcome: **policy corrected** — the first pass ratified its own author's fresh decision; two author challenges exposed the tailoring; the corrected rule replaces the absolute.

## First pass (recorded as the failure specimen)

The initial audit derived requirements (gate-path latency, survivability, byte fidelity, supply chain, installability) and prior art (git, ensurepip, uv, cloud-init) that concluded: keep zero-dep, add a lazy-import rule and a vendoring escape hatch. Verdict looked like refinement; it was ratification.

## Challenge 1: "requirements and prior art were tailored to the conclusion" — sustained

Three loads of tailoring found on re-examination:

1. **R1 smuggled the conclusion.** "Gate-path latency ≈ stdlib import cost" conflates *having* a dependency with *importing it on the gate path*. Module structure decides import cost, not the dependency list. Honestly derived, R1 yields a lazy-import rule, not a dependency ban. Nothing was measured (no CLI startup number, no import-cost number) — in a session that measured everything else before recommending.
2. **Prior art was curated.** The zero-dep icons were cited; the contrary corpus was omitted — including the closest analogues to this project: sigstore-python, in-toto, the TUF reference implementation — supply-chain **trust** tools, all dependency-rich. Worse, the ensurepip/pip citation conceals that pip's actual solution is vendoring ~20 libraries: dependencies by another name, quietly repackaged as the first pass's "escape hatch". Mechanism of failure: prior art recalled from memory instead of dispatched to research — recall selects for confirmation.
3. **The fidelity argument pointed the other way on same-day evidence.** Hours earlier, mutation testing found 19 surviving mutants in the hand-rolled fuzzy-matcher boundaries. Battle-tested parsers amortize fidelity bugs across their user base; unaudited first-party code is still unaudited code. The coercion argument indicts pydantic's default mode, not "libraries".

## Challenge 2: "isn't a tried-and-true library always preferred to homebrew?" — no; the test is contract match

"Tried-and-true" certifies the **library's** contract, not yours. Three questions:

1. Is the problem commodity and hard-to-get-right (timezones, unicode, crypto, TLS, full YAML)? → library, near-unconditionally.
2. Does the library implement the contract you need, or a different one you must then defend against?
3. Must the behavior stay frozen under you (gate-closing semantics)? → pin; vendor when pinning isn't enough.

Caveat on "tried-and-true" itself: it describes the past (xz-utils was tried-and-true the week it shipped a backdoor); popularity amortizes bug risk, not supply-chain or abandonment risk.

## Case applications

| Case | Verdict | Named contract (mis)match |
|---|---|---|
| Frontmatter (pyyaml) | homebrew stands | PyYAML is tried-and-true *at YAML 1.1*: `no`→`False`, auto-datetime — the library's correctness IS the laundering for a byte-faithful layer. Residual: our subset must stay ⊂ what Obsidian parses (split-brain risk, lintable). |
| Registry XML (defusedxml) | **flip: admit** | Parsing externally-influenced XML is commodity-hard; the first pass's noqa was the old policy defending itself. Admitted as first pinned runtime dep, lazy-imported. |
| Percent-codec | mostly stdlib | `urllib.parse.quote` already emits canonical uppercase `%HH`; ours should be a thin wrapper adding round-trip validation. If it's more than that, that's a finding. |
| Fuzzy quote anchoring | homebrew stands, humbled | No tried-and-true library implements W3C-style robust anchoring with NFKC selectors (RapidFuzz sells similarity, not anchoring). Honest fix: reference-vector tests against the W3C algorithm — the 19 survivors are the evidence this is owed. |
| pydantic | rejection stands, narrowed | Coercing, exception-based validation vs four-state reporting; weight on a per-invocation CLI. Not "libraries launder data". |

## Corrected policy (replaces spec §8's absolute)

**Dependency discipline, not dependency count**: minimal, pinned, audited runtime dependencies admitted case-by-case by contract match — *default to the library for commodity hard problems; homebrew only when the contract mismatch can be named out loud* — with nothing heavy imported on the gate path (lazy-import capability deps; hooks pay CLI startup per tool call), optional extras lazy and feature-detected, vendoring preferred where behavior must stay frozen. Zero-deps-so-far was the rule's *output* for a stdlib-shaped codebase, never the rule.

The distinction has teeth: a necessity gets cited to block a genuinely needed dep; a discipline gets reopened case-by-case with the mismatch named.

## Applied outcomes

- Spec §8 sentence rewritten to the corrected rule (this document linked).
- Plan Q Task 2: S314 resolved by admission — `defusedxml==0.7.1` becomes core's first pinned runtime dependency, lazy-imported at the parse site; noqa removed from the plan.
- Spec §10 evidence-shape entry: pydantic rejection re-grounded on the narrow contract argument.
- Backlog: W3C reference-vector tests for the selectors module.

## Method note (why this document exists)

The failure specimen is retained deliberately: a rethink audit run by the author of the decision, hours after the decision, with prior art from recall, converged on the author's conclusion. The corrective was external challenge. Where the stakes warrant it, dispatch prior-art to research and let the requirements be written before rereading the decision.
