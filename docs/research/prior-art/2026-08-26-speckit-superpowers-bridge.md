# speckit-superpowers-bridge: pinned-commit read

Disposition: historical (2026-09-06) [should-be-scoping-review]

Research note, 2026-08-26. Resolves
[Companion: speckit-superpowers-bridge pinned-commit read](https://github.com/eranroseman/knowledge-harness/issues/57)
and feeds the front-door decision in
[Companion: design spec](https://github.com/eranroseman/knowledge-harness/issues/58).

**Recommendation: decline Spec Kit through this bridge as the companion's front
door, and do not vendor the bridge.** The repository demonstrates how a
downstream consumer can give Spec Kit's design artifacts to Superpowers without
teaching either upstream about the other. It does not provide a
companion-plugin front door: it is a per-project Spec Kit extension, requires
Spec Kit and Superpowers to be provisioned separately, and installs
agent-facing commands only through Spec Kit's active integration. Its released
prompt route also differs materially from its source-checkout route. The useful
prior art is the ownership seam, not the workflow dependency or this
implementation.

## Method and pinned sources

This read used primary sources only:

- `lihan3238/speckit-superpowers-bridge` at
  [`8204959a23fe774bff169350bb8804dbf1e2051e`](https://github.com/lihan3238/speckit-superpowers-bridge/tree/8204959a23fe774bff169350bb8804dbf1e2051e),
  the repository's `main` tip fetched on 2026-08-26. Its manifest identifies the
  payload as bridge version 1.2.0.
- `github/spec-kit` tag `v0.16.4` at
  [`d1f50fcbe684a4222059c4ba7f2d7eabcca87402`](https://github.com/github/spec-kit/tree/d1f50fcbe684a4222059c4ba7f2d7eabcca87402),
  the bridge's recorded Spec Kit baseline
  ([version record](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/.specify/extensions/speckit-superpowers-bridge/verified-versions.json#L1-L7)).
- `obra/superpowers` version 6.3.0 at
  [`b36e0829c6d0140e93cfef2ca599b1b07d4a7797`](https://github.com/obra/superpowers/tree/b36e0829c6d0140e93cfef2ca599b1b07d4a7797),
  the same record's Superpowers baseline.
- `mattpocock/skills` at
  [`6654f6b60cd9d5be8b54c6fafe44346dabeb3b76`](https://github.com/mattpocock/skills/tree/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76),
  for the current `grilling`, `grill-with-docs`, and `to-spec` texts used by the
  existing companion analysis.

I also ran `bash tests/run-all.sh` in the pinned bridge checkout. All eight bash
smoke files passed, including 26 bridge-status cases, the five guard rules,
handoff shape, implement-hook dispatch, deterministic release packaging, and
path portability. That run validates the checked-out bash mechanics; it is not
a live Claude Code, Codex, PowerShell, macOS, or end-user install test. The
[test entrypoint](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/tests/run-all.sh#L1-L35)
runs every `tests/test-*.sh` file sequentially.

## What the repository packages

The shipped object is a **Spec Kit extension ZIP**, not a Claude Code plugin,
Codex plugin, or standalone skill pack. Its `extension.yml` declares one
`process` extension, a Spec Kit floor of `>=0.8.10`, three commands (`handoff`,
`guard`, and `execute`), and five Spec Kit lifecycle hooks. Four hooks call the
guard before Spec Kit phases; `after_tasks` creates the handoff
([manifest](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/.specify/extensions/speckit-superpowers-bridge/extension.yml#L3-L69)).

The release builder copies `extension.yml`, `verified-versions.json`, the three
command documents, both bash and PowerShell script directories, and repository
documentation into a deterministic ZIP. It does **not** copy the source
checkout's `.agents/skills/` or `.claude/skills/` mirrors
([release builder](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/scripts/release/build-extension-zip.sh#L42-L60),
[archive construction](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/scripts/release/build-extension-zip.sh#L77-L106)).
The bridge's execute command says fresh installs instead let Spec Kit generate
agent-native skills from the command documents; the hand-authored peers exist
only for this source repository
([execute command](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/.specify/extensions/speckit-superpowers-bridge/commands/speckit.speckit-superpowers-bridge.execute.md#L19-L35)).

That packaging choice creates two prompt surfaces. The source-only Codex and
Claude peers contain a ten-step orchestrator that explicitly invokes
`superpowers:executing-plans` and then verification, review, and branch
finishing
([source-only Codex peer](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/.agents/skills/speckit-superpowers-bridge/SKILL.md#L17-L40)).
The authoritative fresh-install skill is generated from the packaged execute
command. That command runs a guard *named for* `executing-plans`, then says to
execute `tasks.md` with Superpowers discipline; its required-skill list names
TDD, debugging, verification, review, and branch finishing, but never instructs
the agent to invoke `executing-plans` or `subagent-driven-development`
([packaged behavior](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/.specify/extensions/speckit-superpowers-bridge/commands/speckit.speckit-superpowers-bridge.execute.md#L7-L15),
[packaged discipline](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/.specify/extensions/speckit-superpowers-bridge/commands/speckit.speckit-superpowers-bridge.execute.md#L123-L133)).
The parity smoke test compares only skill-directory IDs, not prompt content
([test scope](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/tests/test-claude-codex-skill-parity.sh#L1-L16),
[set comparison](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/tests/test-claude-codex-skill-parity.sh#L38-L66)).
The passing suite therefore does not establish equivalence between the route
advertised in the README/source peers and the route installed from the ZIP.

Spec Kit confirms that routing model. It writes Claude skills under
`.claude/skills` and Codex skills under `.agents/skills`, but installed
extensions register artifacts only for the current default integration. Adding
a second integration does not register the extension there; `specify integration use` or `switch` must make that integration active and rescaffold
the extension
([integration paths](https://github.com/github/spec-kit/blob/d1f50fcbe684a4222059c4ba7f2d7eabcca87402/docs/reference/integrations.md#L3-L17),
[install behavior](https://github.com/github/spec-kit/blob/d1f50fcbe684a4222059c4ba7f2d7eabcca87402/docs/reference/integrations.md#L83-L100),
[activation behavior](https://github.com/github/spec-kit/blob/d1f50fcbe684a4222059c4ba7f2d7eabcca87402/docs/reference/integrations.md#L136-L148)).
The bridge can therefore carry state between agents in one repository, but one
extension install is not a simultaneous dual-harness distribution mechanism.

The manifest also does not install or declare Superpowers as a dependency. It
declares only the Spec Kit version and shell tools; the generated bridge skill
states separately that Superpowers skills must already be available
([requirements](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/.specify/extensions/speckit-superpowers-bridge/extension.yml#L16-L27),
[Codex skill contract](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/.agents/skills/speckit-superpowers-bridge/SKILL.md#L1-L15)).
On bash, `jq` is operationally required even though the cross-platform manifest
marks each shell tool optional: the guard exits when `jq` is absent
([guard dependency check](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/.specify/extensions/speckit-superpowers-bridge/scripts/bash/guard-command.sh#L20-L35)).

## How it routes ownership

The bridge assumes that Spec Kit already owns the feature's design. The normal
route creates `spec.md`, then `plan.md`, then `tasks.md`; Spec Kit's
`after_tasks` hook calls the bridge handoff command. The handoff script records
the feature directory, canonical artifact paths, `supersedes: ["speckit.implement"]`, `executor: "superpowers"`, capabilities, state,
artifact owner, review-only agents, and artifact hashes in
`.specify/superpowers-handoff.json`
([handoff command](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/.specify/extensions/speckit-superpowers-bridge/commands/speckit.speckit-superpowers-bridge.handoff.md#L5-L44),
[JSON writer](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/.specify/extensions/speckit-superpowers-bridge/scripts/bash/update-handoff.sh#L270-L304)).
The states are `ready`, `executing`, `blocked`, and `complete`. A write with an
existing feature directory copies the current Spec Kit artifacts into a
snapshot, and every write appends a handoff event; executing and complete
writes also snapshot SHA-256 values
([state validation and snapshots](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/.specify/extensions/speckit-superpowers-bridge/scripts/bash/update-handoff.sh#L37-L47),
[snapshot and hash work](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/.specify/extensions/speckit-superpowers-bridge/scripts/bash/update-handoff.sh#L215-L268)).

After the handoff, both prompt surfaces read the canonical documents, dispatch
other extensions' `before_implement` and `after_implement` hooks, and update
the state at lifecycle boundaries
([hook dispatch contract](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/.agents/skills/speckit-superpowers-bridge/SKILL.md#L42-L82)).
They differ at the execution core. A release install tells the active agent to
drive tasks while invoking individual discipline skills. The source checkout's
short peer instead invokes `executing-plans` and claims that skill dispatches
TDD and debugging before the wrapper invokes verification, review, and branch
finishing. The bridge contributes no implementation code for those disciplines;
the divergence is in its orchestration prompts.

The source-only call graph is itself less clean than its summary. Superpowers
6.3.0 says Claude Code and Codex have subagents and should use
`subagent-driven-development` **instead of** `executing-plans`. If the agent
does execute `executing-plans` directly, that skill ends by invoking
`finishing-a-development-branch`
([upstream executor](https://github.com/obra/superpowers/blob/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/skills/executing-plans/SKILL.md#L8-L38)).
If it redirects, `subagent-driven-development` performs a broad final review
and also ends with `finishing-a-development-branch`
([upstream SDD terminus](https://github.com/obra/superpowers/blob/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/skills/subagent-driven-development/SKILL.md#L86-L120)).
The source-only bridge wrapper then separately invokes verification, code
review, and branch finishing. Literal compliance therefore either finishes the
branch before the wrapper's review, or repeats final review/finishing after SDD.
The bridge's own 6.3.0 audit checked that six skill names and the `tasks.md`
consumer boundary still existed; it did not analyze these nested terminal
steps
([bridge compatibility rationale](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/specs/018-release-0-16-4-hardening/research.md#L89-L97)).
The passing smoke suite does not execute one skill prompt from another, so this
remains a source-level routing conflict rather than a reproduced provider run.

The guard encodes the collision policy in five branches:

1. deny `speckit.implement` while the handoff is executing;
2. deny Superpowers `brainstorming` and `writing-plans` once both Spec Kit
   `spec.md` and `plan.md` exist;
3. deny `speckit.constitution` while executing;
4. allow every other `speckit.*` action; and
5. allow everything else.

Every check appends a decision to `bridge-events.jsonl`
([guard implementation](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/.specify/extensions/speckit-superpowers-bridge/scripts/bash/guard-command.sh#L40-L94)).
These are hardcoded decisions, but they are not an ambient interceptor for
arbitrary skill calls. The extension registers the guard only on named Spec Kit
hooks, while the execute command and generated skill instruct the agent to call
or respect it. A direct Superpowers invocation outside those paths reaches no
guard hook shown in the manifest. This is an inference from the complete
manifest and call sites, not a live attempt to make an agent violate the rule.

The ownership barrier is deliberately permeable. The guard allows
`speckit.clarify`, `speckit.plan`, and `speckit.tasks` even while Superpowers is
executing. If artifacts change after the executing snapshot, completion emits
an advisory drift warning and event; it does not fail the transition. A
`complete` handoff with unchecked non-deferred tasks likewise warns without
blocking
([allow branches](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/.specify/extensions/speckit-superpowers-bridge/scripts/bash/guard-command.sh#L52-L71),
[drift behavior](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/.specify/extensions/speckit-superpowers-bridge/scripts/bash/update-handoff.sh#L337-L354),
[pending-task warning](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/.specify/extensions/speckit-superpowers-bridge/scripts/bash/bridge-state.sh#L72-L93)).

## Front-door comparison

The three candidates own different amounts of the lifecycle; they are not
equivalent wrappers around one interview.

| Candidate                   | Decision work                                                                                                                                                                                                                                                                        | Durable output                                                                                                                                                                                                | Terminal route                                                                                                                                                              | Fit after an exhaustive grill                                                                                                                                    |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `grilling` + `to-spec`      | `grilling` explores the complete dependency frontier in rounds, delegates fact-finding, and stops only when no decision remains. `to-spec` says not to interview again, though it retains one user confirmation of testing seams.                                                    | One tracker spec using project glossary and ADRs, with problem, solution, user stories, implementation and testing decisions, out-of-scope, and no stale code paths/snippets. It applies `ready-for-agent`.   | The tracker state hands execution to the project's separate plan or ticket route.                                                                                           | Strongest fit: synthesis follows the interview instead of reopening it.                                                                                          |
| Superpowers `brainstorming` | Classifies the request as spike, bounded, or architectural; all paths require approval. The architectural path asks questions, compares approaches, presents design sections, self-reviews the written spec, gets another user approval, then calls `writing-plans`.                 | Chat-only intent for bounded work; a committed design document for architectural work.                                                                                                                        | `writing-plans` is the sole architectural successor.                                                                                                                        | It repeats discovery and approval already performed by a completed grill; its self-review and approach comparison remain useful patterns.                        |
| Spec Kit through the bridge | `speckit.specify` derives a spec from a description, may ask up to three clarifications, and runs a checklist loop. Optional `speckit.clarify` scans a broad taxonomy and asks up to five more questions, one at a time. `plan` and `tasks` then add technical and execution detail. | A per-feature directory: `spec.md`, requirements checklist, `plan.md`, `research.md`, `data-model.md`, optional contracts, `quickstart.md`, and `tasks.md`, plus bridge state, snapshots, hashes, and events. | The bridge supersedes `speckit.implement`. Its packaged command drives tasks with individual Superpowers disciplines; its source-only peer instead calls `executing-plans`. | Valid only if the project first chooses Spec Kit's artifact system. After a grill, its clarification stages and parallel spec vocabulary duplicate settled work. |

The first row follows the pinned
[`grilling`](https://github.com/mattpocock/skills/blob/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/productivity/grilling/SKILL.md#L6-L28)
and
[`to-spec`](https://github.com/mattpocock/skills/blob/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/engineering/to-spec/SKILL.md#L7-L75)
contracts; `grill-with-docs` itself is only a two-skill dispatcher
([source](https://github.com/mattpocock/skills/blob/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/engineering/grill-with-docs/SKILL.md#L1-L7)).
The second follows Superpowers' three-path hard gate and architectural sequence
([classification and gate](https://github.com/obra/superpowers/blob/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/skills/brainstorming/SKILL.md#L8-L52),
[architectural checklist](https://github.com/obra/superpowers/blob/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/skills/brainstorming/SKILL.md#L75-L103),
[self-review and handoff](https://github.com/obra/superpowers/blob/b36e0829c6d0140e93cfef2ca599b1b07d4a7797/skills/brainstorming/SKILL.md#L202-L231)).
The third follows Spec Kit's own specification and clarification workflows
([spec generation and three-question limit](https://github.com/github/spec-kit/blob/d1f50fcbe684a4222059c4ba7f2d7eabcca87402/templates/commands/specify.md#L56-L142),
[quality loop](https://github.com/github/spec-kit/blob/d1f50fcbe684a4222059c4ba7f2d7eabcca87402/templates/commands/specify.md#L144-L234),
[five-question clarification loop](https://github.com/github/spec-kit/blob/d1f50fcbe684a4222059c4ba7f2d7eabcca87402/templates/commands/clarify.md#L56-L180),
[task artifact contract](https://github.com/github/spec-kit/blob/d1f50fcbe684a4222059c4ba7f2d7eabcca87402/templates/commands/tasks.md#L61-L93)).

Spec Kit's larger artifact set is real value when a project wants Spec Kit as
its system of record. Its plan phase explicitly produces research, data-model,
contract, and quickstart artifacts, and its tasks phase maps them into
dependency-ordered user-story work
([plan outputs](https://github.com/github/spec-kit/blob/d1f50fcbe684a4222059c4ba7f2d7eabcca87402/templates/plan-template.md#L39-L57),
[task inputs and organization](https://github.com/github/spec-kit/blob/d1f50fcbe684a4222059c4ba7f2d7eabcca87402/templates/tasks-template.md#L6-L44)).
That value is also why the bridge is unsuitable as an invisible companion
front door: adopting it chooses another artifact model, command vocabulary,
project bootstrap, state directory, and upgrade surface. The bridge does not
hide that decision; it only makes the Spec Kit-to-Superpowers seam explicit.

## Disposition for Companion: design spec

**Decline the bridge and Spec Kit from the companion's default front door.** Do
not vendor the repository, repackage its extension, or make the companion
installer provision Spec Kit. Keep the companion's front door in its native
skill/tracker model, where an exhaustive decision pass feeds one synthesis and
then the existing planning or ticket route. The repository's
[MIT license](https://github.com/lihan3238/speckit-superpowers-bridge/blob/8204959a23fe774bff169350bb8804dbf1e2051e/LICENSE)
permits reuse; this decline is about ownership, distribution, and the divergent
execution prompts, not licensing.

Adopt one architectural lesson without adopting code: **the consumer of two
upstreams owns a bounded, named handoff at their collision point.** If a future
repository independently selects Spec Kit, treat this bridge as an optional
external integration: Spec Kit owns `spec.md`/`plan.md`/`tasks.md`; Superpowers
owns implementation discipline; the bridge owns only their handoff. Do not run
that route in parallel with the companion's own design front door.

The evidence also suggests two requirements for any companion-owned bridge:

1. State which owner is canonical at each phase, and suppress the losing route
   after the handoff.
2. Put enforcement on a host-visible invocation boundary if it must be hard.
   A callable guard plus prompt instructions is a policy with tests, not a
   universal interceptor.

## Uncertainties and negative knowledge

- I did not run a live Claude Code or Codex feature cycle, a real
  `specify extension add` install, native PowerShell, or native macOS. The
  recommendation rests on source shape and the passing local bash suite, not
  behavioral quality claims about generated specs.
- Spec Kit documents active-integration-only extension registration. It may
  leave previously generated files present after switching, so both harness
  directories can coexist after sequential activation; the source does not
  support the stronger claim that one extension installation populates both
  integrations immediately.
- No manifest or call site at the pin connects the guard to arbitrary
  Superpowers skill invocation. If a host supplies an undocumented generic
  interception layer, this read did not find or test it.
- I did not render the installed skill in a fresh Spec Kit project. The release
  builder and execute command establish that the local peers are absent and the
  command is the generation source; a live install would be needed to compare
  every generated byte.
- The bridge records `verified-versions.json`, but compatibility evidence is
  repository-owned. This investigation verified source contracts at the pins;
  it did not independently reproduce every platform or agent row.
