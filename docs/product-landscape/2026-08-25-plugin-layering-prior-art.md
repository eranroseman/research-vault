# Prior art: layering a mandatory process engine over an opt-in skill pack

Research note, 2026-08-25. Feeds the prior-art section of the audit that follows
`2026-08-25-coding-companion-plugins-comparison.md`'s layered verdict (superpowers'
execution core owns planned-code machinery; mattpocock owns config, planning
surfaces, domain language, and the tracker). Two questions: (1) has anyone
publicly discussed or built this specific composition; (2) what does other
software architecture say about where the seam between a mandatory engine and
an opt-in policy layer belongs.

## 1. Public discussion of composing the two packs

**Direct blog comparisons exist, and both argue against composing them.**
[nocoders.com, "Superpowers vs Matt Pocock's skills: two opposite bets on who
runs your agent"](https://www.nocoders.com/blog/superpowers-vs-pocock-agent-skills/)
frames the split exactly on the mandatory/opt-in axis this audit uses —
superpowers' `SessionStart` hook and 1%-rule ("If you think there is even a 1%
chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke
the skill") against mattpocock's "no session hook; nothing gets injected at
startup" — and states the decision as exclusive: "The real decision isn't
'which repo.' It's: do you want a system that enforces a process, or a toolkit
you drive?" [zenn.dev/kanagen's comparison](https://zenn.dev/kanagen/articles/claude-code-skills-superpowers-vs-mattpocock?locale=en)
goes further, naming coexistence itself as the problem: "Although the majority
of functional coverage does not overlap, coexistence is difficult in
practice. The reason is not functional duplication but philosophical
conflict" — and concludes readers "should choose one or the other," blaming
superpowers' 1% rule for false-positive triggering against mattpocock's
opt-in model. Both posts assign superpowers "how to operate" (execution
process) and mattpocock "what to build" (domain language, CONTEXT.md,
tracker) — the same split this audit's verdict uses — but both treat that
split as grounds to pick one, not to layer both. This is the sharpest tension
this research turned up against the audit's layered verdict, and it is
external commentary, not a stated policy of either project.

**GitHub-native evidence corroborates the conflict empirically, but not
unanimously.** In mattpocock/skills' own Discussions (enabled;
`obra/superpowers` has Discussions disabled — `has_discussions: false` via
`gh api repos/obra/superpowers`), discussion
[#257, "Can /superpowers be complementary?"](https://github.com/mattpocock/skills/discussions/257)
asks this exact question. One reply (user `betaxD`) reports running
superpowers and "GSD" together and having to "tell the model which one you
want it to use," and once left it unsupervised long enough that "each one had
to get context all again" and simple tasks fanned out into unwanted
subagents. Another reply (user `matttk`, unaffiliated with either project)
reports the collision from the audit's own framing: after pairing them,
"Superpowers... would load up brainstorming and start making a multi-step
process to plan things out with a design doc, etc., when really all I needed
was for Claude to just execute on the already-laid-out issue" — mandatory
injection firing against work mattpocock's tracker had already specified — so
he turned superpowers off. This is the same failure mode the internal
comparison note (`2026-08-25-coding-companion-plugins-comparison.md`, frictions
§1) names as "SessionStart injection pressures every session toward skill
invocation, wrong-shaped for [some] workloads," mitigated there via per-skill
`skillOverrides` rather than by uninstalling either plugin — i.e., this repo
already has a specific, tested answer to the exact complaint that leads
outside commentary to recommend "pick one."

Pulling the other way: `obra/superpowers` issue
[#1007, "Composing superpowers with team-specific skills"](https://github.com/obra/superpowers/issues/1007)
(closed, not-planned) is the maintainer's own stated position on
composability in general. A user asked for a `pack.json` so superpowers could
be installed alongside other skill sources via a third-party composer tool
(`aipack`); a comment on the same thread (user `LAN813-git`) describes having
"superpowers, mattpocock/skills, planning-with-files, and humanizer-zh
installed separately" and building **Super Powers Plus**, which explicitly
fuses superpowers and mattpocock skill files pairwise (`diagnose`, `tdd`,
`review` each merge "the best of sp + mp into one file") rather than running
both packs' raw trigger machinery side by side — implicitly conceding the
blog posts' point that raw coexistence is the hard part, while insisting
fusion still counts as composing: "Not trying to replace superpowers — it's
still the foundation. Just making it composable with the rest of the
ecosystem." The maintainer's close reason cites the project's own
third-party-dependency policy and a direct precedent: "That also mirrors how
[#163](https://github.com/obra/superpowers/issues/163) (superpowers +
spec-kit) played out: the tools compose fine, and the bridging logic lives in
the consuming tool rather than upstream" — i.e. superpowers' stated position
is that composability is real but is the consumer's problem to solve, not a
feature core should add.

Separately, two of superpowers' own bug-report issues
([#2097](https://github.com/obra/superpowers/issues/2097),
[#2120](https://github.com/obra/superpowers/issues/2120)) list `superpowers`
and `mattpocock-skills` side by side in "all plugins installed" fields for
real, active sessions, with no conflict flagged in either report — weak but
real evidence that at least some users run both without the collision
matttk hit, presumably because their tasks didn't cross the
already-planned-work trigger case.

**Downstream tools that had to reconcile both packs mechanically** (not
opinion pieces, but working code):

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

Net: every downstream project that tried raw side-by-side installation
(gitflow-cli, the Discussions #257 reporters) either detected-and-picked-one
or hit the trigger collision; only fusion (mur-run/mur's merge, Super Powers
Plus's file-level fusion) or a per-skill override (this repo's own mitigation)
avoided it. That is a real, external data point the audit should weigh: the
layered verdict here works because the mitigation for the one recorded
layer-fight (grilling vs. brainstorming, settled in settings) is already
applied — the same fix pattern nobody in the wild seems to have reached for
before concluding "pick one."

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
