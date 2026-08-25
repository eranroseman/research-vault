# Prior art: layering a mandatory process engine over an opt-in skill pack

Research note, 2026-08-25. Feeds the prior-art section of the audit that follows
`2026-08-25-coding-companion-plugins-comparison.md`'s layered verdict (superpowers'
execution core owns planned-code machinery; mattpocock owns config, planning
surfaces, domain language, and the tracker). Two questions: (1) has anyone
publicly discussed or built this specific composition; (2) what does other
software architecture say about where the seam between a mandatory engine and
an opt-in policy layer belongs.

## 1. Public discussion of composing the two packs

Neither project's own README stakes a position on composing with the other by
name. **obra/superpowers**'s README presents itself as a self-contained
methodology — "a complete software development methodology for your coding
agents, built on top of a set of composable skills" — with mandatory triggering
("the agent checks for relevant skills before any task. Mandatory workflows,
not suggestions") and no discussion of interoperating with external plugin
ecosystems ([github.com/obra/superpowers, README](https://github.com/obra/superpowers/blob/main/README.md)).
**mattpocock/skills**'s README does stake out a scope position, but as a
refusal rather than a composability story: "Approaches like GSD, BMAD, and
Spec-Kit try to help by owning the process. But while doing so, they take away
your control and make bugs in the process hard to resolve" — the pack commits
to staying "small, easy to adapt, and composable" instead
([github.com/mattpocock/skills, README](https://github.com/mattpocock/skills/blob/main/README.md)).
Neither repo's issue tracker has an open discussion of the other by name (a
GitHub code search of each repo's issues for the other project's name returns
only incidental hits, no design discussion).

The concrete grappling with this seam happens downstream, in tools that
consume both packs and had to reconcile them:

- **byx-darwin/gitflow-cli**, issue [#141](https://github.com/byx-darwin/gitflow-cli/issues/141)
  and PR [#147](https://github.com/byx-darwin/gitflow-cli/pull/147): a
  workflow CLI hardcoded to `superpowers:brainstorming` /
  `superpowers:writing-plans` / `superpowers:subagent-driven-development` added
  mattpocock/skills support. The issue's own comparison table concludes the two
  are not interchangeable by name — "两个来源存在行为差异，不是简单同名替换" (the
  two sources differ in behavior; this isn't a same-name substitution) —
  mapping brainstorming→grilling+to-spec, writing-plans→to-tickets,
  subagent-driven-development→implement+tdd, and noting mattpocock's `to-spec`
  overlaps with the CLI's own issue-creation responsibility. The chosen design
  is **mutually exclusive detection**, not layering: "假设用户只安装一个来源，只检测
  「哪个在场」，不处理共存优先级" (assume the user installs only one source; detect
  which is present, don't handle coexistence priority) — the opposite of this
  repo's stance that both can run side by side because they own different layers.
- **mur-run/mur**, PR [#751](https://github.com/mur-run/mur/pull/751):
  internalizes skills from both packs into "one canon per topic," and adds a
  detection switch (`skills.dev_discipline_index: auto|always|never`) that
  hides its own built-in hub when the superpowers plugin is already installed —
  a "never-shadow" policy built specifically to avoid two mandatory-feeling
  systems fighting over the same trigger surface.
- **EricTechPro/super-board**, PR [#14](https://github.com/EricTechPro/super-board/pull/14):
  a full migration from superpowers to mattpocock/skills, not a layered
  composition, but its migration table is independent corroboration of the
  engine/pack split: everything with a mattpocock equivalent was swapped
  (`writing-plans`→`to-spec`, `systematic-debugging`→`diagnosing-bugs`, etc.),
  while three skills were explicitly **kept** because "Matt's pack has no
  equivalent" — `verification-before-completion`, `shape`, `clarify`. The one
  named execution-discipline skill in that kept list,
  `verification-before-completion`, is exactly the kind of machinery this
  repo's audit assigns to the mandatory engine.

No blog post, changelog, or discussion thread was found that frames this as a
general "mandatory-hook engine + opt-in skill library" composability question;
the evidence is three independent repos independently hitting the same seam
from different angles (compatibility, internalization, migration) and landing
on different resolutions — mutual exclusion, shadow-suppression, and full
replacement, respectively. None of the three adopted this repo's layered
coexistence, which is worth noting as a gap the audit is filling rather than
following.

## 2. General precedent: mandatory engine vs. opt-in policy layer

Across ecosystems that separate a fixed core from swappable extensions, the
seam sits wherever a **cross-cutting invariant** (consistency, safety, or
interoperability that must hold identically for every extension) needs a
single arbiter. Everything downstream of that invariant — domain-specific
behavior that only needs to be correct for its own case — is left to the
extension.

| System | Mandatory side (must be universal) | Opt-in side (safely varies) | Forcing property |
|---|---|---|---|
| LSP | Base protocol: JSON-RPC transport, message lifecycle, capability negotiation | Each language server's actual analysis (completion, diagnostics, hover) | Solves the M editors × N languages problem — a shared wire format is what collapses M×N integrations to M+N; if negotiated per pair, the problem recurs ([LSP overview](https://microsoft.github.io/language-server-protocol/overviews/lsp/overview/), [3.17 spec](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/)) |
| Terraform | Core: state tracking, dependency graph, plan/apply ordering, RPC orchestration | Providers: resource CRUD against one vendor's API | Plan/apply safety requires one arbiter of ordering and state locking across every resource in a graph, regardless of which vendors are mixed in it ([How Terraform works with plugins](https://developer.hashicorp.com/terraform/plugin/how-terraform-works)) |
| Kubernetes | Control plane: API server, watch/diff/act reconciliation loop | CRDs/operators: what "desired state" means and how to converge toward it for one application | Convergence guarantees depend on every controller obeying the same reconciliation contract; the domain knowledge of how to reconcile one application can't be generalized into the platform ([Operator pattern](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/)) |
| Unix | Kernel-level system calls: `fork`, `execute`, `wait`, `pipe`, the file system | Userland commands (shell, `ls`, etc.) — ordinary executable files | The 1974 paper treats fork/execute/wait/pipe as system primitives everything else is built from, while noting commands need not even live in a special directory to run — they're ordinary, replaceable programs built on the primitives (Ritchie & Thompson, "The UNIX Time-Sharing System," *CACM* 17:7, July 1974, §§3, 5; [ACM DOI](https://dl.acm.org/doi/10.1145/361011.361061)) |
| CI (GitHub Actions) | Runner: provisions the job's execution environment and runs every step through the same lifecycle | Actions: reusable, swappable units of step logic | Every job needs a guaranteed, uniform execution context (one runner, one job at a time, same triggering/lifecycle semantics) independent of what any given step does ([Understanding GitHub Actions](https://docs.github.com/en/actions/about-github-actions/understanding-github-actions)) |
| ESLint | Core linter: parses the AST, traverses it, emits per-node events, resolves config | Rules/plugins: inspect the AST for one pattern and report | Rules can only be pluggable if every one gets an identical AST and traversal contract from the core; that contract has to be enforced in exactly one place ([ESLint architecture](https://eslint.org/docs/latest/contribute/architecture/)) |

The common shape: the mandatory side owns whatever must be identical for the
extension mechanism to be trustworthy at all (a shared wire protocol, a single
state arbiter, one reconciliation contract, the privilege boundary, a uniform
execution context, one AST contract). The opt-in side owns knowledge that is
correct only relative to one adopter's domain, and generalizing it into the
mandatory layer would either be impossible (N languages, N cloud APIs, N
applications) or would re-introduce the coordination problem the mandatory
layer exists to remove. This matches the shape of the audit's proposed split:
superpowers' execution core (review/verification/finishing) is the piece that
must behave identically regardless of which repo or tracker is in play;
mattpocock's tracker/config/domain-language layer is correct only relative to
one repo's conventions.
