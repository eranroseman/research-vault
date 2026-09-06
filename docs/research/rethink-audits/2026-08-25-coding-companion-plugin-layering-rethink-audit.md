# Rethink audit — coding-companion plugin layering

Disposition: historical (2026-09-06)

Clean-slate design audit of the tooling architecture behind [docs/product-landscape/2026-08-25-coding-companion-plugins-comparison.md](../../product-landscape/2026-08-25-coding-companion-plugins-comparison.md)'s layered verdict (superpowers' execution core owns planned-code machinery; mattpocock/skills owns config, planning surfaces, domain language, and the tracker). Method: rethink-audit (requires → prior-art → design → gap → migrate → trade-offs). Prior-art sourcing: [docs/product-landscape/2026-08-25-plugin-layering-prior-art.md](../../product-landscape/2026-08-25-plugin-layering-prior-art.md) (background research, advisor-corrected mid-run).

## requires:

R1 every code change touching vault invariants (OKF conformance, four-state honesty, deprecate-never-delete, citekey identity — ADRs 0001–0004) gets review that hunts violations specifically, not generic review (`tests` — disarmed-test catch, fail-open guard deletion, None-idiom-as-MATCHED, all from the comparison doc's post-q batch) · R2 planning speaks GitHub Issues — `gh` CLI, triage labels, wayfinder maps, not an ad hoc plan file (`docs` — `docs/agents/issue-tracker.md`) · R3 design/refactor proposals gated against `CONTEXT.md` + `docs/adr/`, exact glossary terms, ADR conflicts flagged not silently overridden (`docs` — `docs/agents/domain.md`) · R4 tooling must not force one workflow shape onto future non-coding sessions sharing the same account (`assumed` — comparison doc's own friction §1) · R5 eliminate the problem before adding a mechanism, a mechanism before a rule, prose last (`docs` — AGENTS.md root line; meta-requirement on the design itself) · R6 completion claims carry MATCHED/UNMATCHED/UNREACHABLE/SKIPPED honesty (`adr` 0002, generalized — comparison doc names this the repo's own unclaimed doctrine, portable past code) · R7 multiple sessions share one checkout; an orchestration layer above single-plan execution is a caller too (`docs` — AGENTS.md parallel-sessions line) · R8 no doctrine duplicated across N skill files (`docs` — writing-for-agents, already adopted per comparison doc's Further Insight §3).

Sweep can't reach: usage of either plugin in the user's other repos (settings are user-global, invisible from here); whether a session actually skips invocation despite hook pressure (gating is prompt-level only, unenforceable from outside the session).

## prior-art:

Cross-ecosystem precedent for where a mandatory-engine/opt-in-layer seam sits (full citations in the prior-art file):

| System         | Mandatory side                                               | Opt-in side                     | Forcing property                                                             |
| -------------- | ------------------------------------------------------------ | ------------------------------- | ---------------------------------------------------------------------------- |
| LSP            | base protocol (transport, lifecycle, capability negotiation) | each language server's analysis | collapses M editors × N languages to M+N                                     |
| Terraform      | core (state, dependency graph, plan/apply ordering)          | providers                       | one arbiter of ordering/locking across every resource in a graph             |
| Kubernetes     | control plane (reconciliation loop)                          | CRDs/operators                  | convergence guarantee needs one contract every controller obeys              |
| Unix           | kernel syscalls (`fork`/`execute`/`wait`/`pipe`)             | userland commands               | primitives everything else is built from; commands are ordinary, replaceable |
| GitHub Actions | runner (execution context, job lifecycle)                    | actions (step logic)            | uniform execution context independent of step content                        |
| ESLint         | core (AST parse/traverse, config resolution)                 | rules/plugins                   | one AST/traversal contract, enforced in exactly one place                    |

Common shape: the mandatory side owns a cross-cutting invariant that must hold identically for every extension; the opt-in side owns knowledge correct only for one adopter. Matches the audit's split — superpowers' execution core must behave identically regardless of repo or tracker; mattpocock's tracker/config/vocabulary is correct only relative to one repo's conventions.

**Real tension, not just confirmation.** Two blog posts ([nocoders.com](https://www.nocoders.com/blog/superpowers-vs-pocock-agent-skills/), [zenn.dev/kanagen](https://zenn.dev/kanagen/articles/claude-code-skills-superpowers-vs-mattpocock?locale=en)) frame the same mandatory/opt-in split this audit uses, then argue against layering it — "philosophical conflict," pick one. Field evidence backs it: mattpocock discussion [#257](https://github.com/mattpocock/skills/discussions/257), user `matttk` — mandatory brainstorming fired against work his tracker had already fully specified; he disabled superpowers over it. Downstream tools that had to reconcile both packs mechanically (gitflow-cli [#141](https://github.com/byx-darwin/gitflow-cli/issues/141)/[#147](https://github.com/byx-darwin/gitflow-cli/pull/147), mur-run [#751](https://github.com/mur-run/mur/pull/751), super-board [#14](https://github.com/EricTechPro/super-board/pull/14)) all reconciled by fusing skill files or picking one outright — none ran raw side-by-side layering.

**Resolution.** Every failure case cited is *unbridged* raw install (both packs installed, nothing reconciling their trigger surfaces). superpowers' maintainer's own stated position (issue [#1007](https://github.com/obra/superpowers/issues/1007)): composability is real, but the bridging logic belongs to the consuming tool, not core — the same conclusion reached independently for issue #163 (superpowers + spec-kit). This repo *is* that consuming tool, already runs a partial bridge (`skillOverrides: grilling → name-only`), and the comparison doc's own validation section shows a full batch executed with both layers live and zero collision — direct session evidence the wild raw-install commentary doesn't have. The layered verdict holds, but it is conditioned on the bridge's coverage, which is incomplete (gap F).

## design:

Vocabulary from codebase-design. Four pieces, not two:

- **Execution-discipline module** — interface: a task in, a reviewed+verified+merged change plus a disposition record out; deep implementation is SDD's fix-loop, model escalation, ledger, "attempted is not addressed." Adapter: superpowers.
- **Repo-policy module** — interface: `docs/agents/*` conventions, label vocabulary, tracker operations. Adapter: mattpocock, same task-entry/disposition-exit seam.
- **Doctrine module** — not an adapter; the invariant both adapters must satisfy (four-state honesty, evidence conventions, deprecate-never-delete). Lives where every session reads it unconditionally — AGENTS.md/CLAUDE.md/ADRs, not behind invocation.
- **The bridge** — this repo's own responsibility per the superpowers maintainer's stated division of labor: reconciling the two adapters' trigger surfaces at their actual collision points. Today it is one override (grilling↔brainstorming). Its thinness is exactly why external raw-install users conclude "pick one."

Deletion test on the first three: pulling any one of them makes real complexity reappear elsewhere (fix-loop rigor, tracker/ticket-graph, four-state propagation without invocation) rather than vanish — three genuine deep modules. "Two adapters means a real seam" confirms the split is load-bearing, not invented to justify three layers. Verdict: layered, per the original comparison doc — conditioned on the bridge being maintained as its own named piece, which the gaps below show it currently isn't.

## gap:

Checked against current state (`~/.claude/settings.json`, `docs/adr/`, `.agents/.skill-lock.json`, project `.claude/settings.json` — absent).

- **A. Doctrine duplicated** — the four-state honesty table is restated in four skills (comparison doc's own Further Insight §3). Violates R8.
- **B. Decision never ratified as an ADR** — `docs/adr/` holds 0001–0004, all vault-domain; the layered-governance verdict itself sits only in `docs/product-landscape/`, which `docs/agents/domain.md`'s "flag ADR conflicts" step does not read. A future domain-modeling pass has nothing to check this decision against.
- **C. "Per-repo" language, global-scope mechanism** — no project-level `.claude/settings.json` exists in this repo; `skillOverrides`/`enabledPlugins` live in `~/.claude/settings.json`, applying to every repo on this account, not just this one.
- **D. Controller seat ungoverned** — comparison doc's own blind spot (a): cross-session ruling, relay protocol, permission hygiene have no owning skill or doctrine.
- **E. Asymmetric update ritual** — superpowers has a named reviewed-upgrade ritual (comparison doc's friction §2); mattpocock's per-skill symlinked copies (`skills.sh`, hash-pinned in `.skill-lock.json`) have none.
- **F. Bridge covers skill-selection collision only, not the ticket-already-specified collision** — matttk's exact failure (mandatory brainstorming firing against fully-specified tracker work) is unmitigated here today. Field-reported externally, not yet suffered internally — matches the comparison doc's own blind spot (b): tracker-mediated execution is untested, Plan W pilot still pending. The most load-bearing finding in this audit: it is the one condition the whole layered verdict depends on.

## migrate:

1. Collapse the four-state table to one canonical reference; per-skill files keep deltas only (closes A).
2. Write `docs/adr/0005-coding-companion-plugin-layering.md`: mattpocock owns config/planning/tracker/domain-language, superpowers owns execution core, this repo's own doctrine binds both (closes B).
3. Either add a project-scoped `.claude/settings.json` pinning what this decision depends on, or add an AGENTS.md line stating the scope is deliberately user-global and why — pick one, don't leave the mismatch unstated (closes C).
4. Bank the controller-seat protocol as the short research note the comparison doc's Further Insight §4 already proposes, before the session's improvised protocol becomes unreconstructable (closes D).
5. Add one line to `docs/agents/` naming what to check on a mattpocock `skills.sh update` — a hash-diff review, mirroring superpowers' reviewed-upgrade ritual (closes E).
6. Checked `skillOverrides`' schema before proposing this: it is a static enum (`on`/`name-only`/`user-invocable-only`/`off`), no conditional form — "skip brainstorming if the ticket is already specified" cannot be a settings mechanism. The bridge has to land as a **rule**, not a mechanism, named honestly against this repo's own eliminate-mechanism-rule ordering: add to `docs/agents/issue-tracker.md` — a `ready-for-agent`-labeled issue *is* the spec; SDD entry goes straight to plan/execute, brainstorming/writing-plans is not re-invoked (closes F).

## trade-offs:

Two upstreams tracked instead of one, doubling upgrade-review — flips only if AFK/tracker workflows stop being used, at which point mattpocock's upkeep cost stops paying for itself. Two vocabularies live in one head (ticket vs. task-brief/ledger) — flips on an actual term-collision mistake; none observed yet per the comparison doc's own validation pass. **No single enforcement point is field-observed, not hypothetical** — `matttk` (discussion #257) actually disabled superpowers over exactly this collision; this repo's exposure is real until migrate step 6 lands. Global settings scope trades per-repo duplication for zero isolation from a future non-coding repo — flips the moment that repo goes active, the exact trigger the comparison doc's friction §1 already names.

**Verdict:** not "already sound" — six divergences found, five ordinary hygiene (A–E), one (F) load-bearing enough to gate the layered verdict's own stated condition (the bridge must actually cover the collision it's supposed to prevent). Layered architecture confirmed as the right target; migrate steps close every gap without deforming it.

______________________________________________________________________

## Amendment, 2026-08-25 — three factual corrections after user verification

Re-verified independently before accepting each, not taken as given.

**1. nocoders mischaracterized.** The prior-art section's "real tension" paragraph states both blog posts "argue against layering it — 'philosophical conflict,' pick one." Only [zenn.dev/kanagen](https://zenn.dev/kanagen/articles/claude-code-skills-superpowers-vs-mattpocock?locale=en) makes that argument. [nocoders.com](https://www.nocoders.com/blog/superpowers-vs-pocock-agent-skills/) is a neutral comparison — "neither bet is wrong" — that never discusses combining the two packs. The claim should have been scoped to zenn alone; nocoders only supplies the shared framing (mandatory-process vs. driven-toolkit), not the anti-layering argument.

**2. obra #1007 quote's provenance undisclosed.** The "bridging logic belongs to the consuming tool, not core" line, and its "#163 played out the same way" gloss, are both from the issue's closing comment — posted by an AI agent acting from the maintainer's account at his direction, not typed by him directly. The citation is accurate to what's on the issue; the provenance wasn't stated in the prior-art section and should have been.

**3. Gap D was already closed when filed.** `docs/research/validation-slice/2026-08-25-controller-protocol-material.md` was committed at 15:07:24 (`0abec75`), 16 minutes before this audit's own commit at 15:23:28 (`e144a4e`) — confirmed via `git log`, not taken on report. Gap D ("controller seat ungoverned") and migrate step 4 ("bank the controller-seat protocol... before it's unreconstructable") describe a gap that no longer existed at filing time.

None of the three change the verdict — design: is still layered, still conditioned on gap F. They correct the audit's record of what it found and when, per this repo's own evidence-honesty doctrine (ADR 0002/0003): the note ships errors as written; corrections append, they don't silently rewrite.
