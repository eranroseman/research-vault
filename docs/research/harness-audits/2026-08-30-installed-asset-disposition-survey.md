# Installed asset disposition survey

**Status: approved by the author 2026-08-31.** No decisions remain open in this document.
**Date:** 2026-08-30 · **Ticket:** [#75](https://github.com/eranroseman/knowledge-harness/issues/75), a `wayfinder:grilling` ticket on map [#53](https://github.com/eranroseman/knowledge-harness/issues/53)

Every plugin and skill installed across Claude Code and Codex, the full upstream `mattpocock/skills` roster including the nineteen not installed here, and the four `harness-backup`-owned skills. Each gets a ladder rung, a bucket where one applies, a sharing verdict, and — for plugins — a fork call.

Companion to the [2026-08-28 alteration-inventory sweep](2026-08-28-alteration-inventory-sweep.md), which asked whether assets had drifted. This asks what to do with them.

**The destination**, per map #53: an installable cross-harness plugin, canonical home for shared authored and deliberately adapted guidance and automation, running on **both Claude Code and Codex**, **reproducing the harness on a fresh machine**, detecting drift, and retiring the private `harness-backup` repository only after verified functional parity.

**Two kinds of claim appear here.** *Measurements* are properties of the installed artefacts, independently verifiable, true regardless of what is decided. *Recommendations* are conclusions drawn from them. Method is in the appendix.

## What needs deciding

**Settled 2026-08-31:** the per-asset recommendations are approved as a set; `caveman` is **recommended**; the fork is **public**; `writing-specs` vendors from **upstream HEAD**; the marketplace is **`eroseman`**; the shared distributable is renamed **`sensemaking`**.

Still open:

Nothing. The marketplace is **`eroseman`**, and the shared distributable is named **`sensemaking`** (both 2026-08-31).

One consequence of a single marketplace: `software-development` will declare dependencies on `sensemaking` and on the `superpowers` fork, and Claude Code resolves a plugin's dependencies **within its own marketplace** unless the root lists others in `allowCrossMarketplaceDependenciesOn`. Hosting all four in `eroseman` makes that allowlist unnecessary. Each plugin keeps its own repository — a marketplace entry carries its own source, as `obra/superpowers-marketplace` demonstrates across ten plugins. Codex does not resolve dependencies at all — verified: `codex plugin add` takes `PLUGIN@MARKETPLACE` or `PLUGIN --marketplace M`, naming the marketplace explicitly per plugin, and neither `codex plugin` nor `codex plugin add` has any dependency concept. So the within-marketplace rule is Claude Code's alone, and on Codex a single marketplace buys only fewer `[marketplaces.*]` registrations for #62 to add and #78 to verify.

## Ground rules

**The ladder, the bucket rule and the `defer` state are on map #53** under *Design doctrine*, with the duplication and fork-obligation doctrines. Not restated here; this survey applies them.

Two points for the tables below. **Buckets attach to rungs 1 and 2 only** — the rungs where something is depended on — and are **required** (the plugin does not work without it), **recommended** (works without it, but a user should have it) or **unrelated** (no relationship to either product; personal harness furniture). Rungs 3–5 have no bucket. And **where a plugin is rung 1 or 2, all its components come across**, so per-skill detail for those rows is informational.

Four author-settled inputs the doctrine does not cover:

**Fork policy is per-plugin with no default.** Each call rests on its own upstream evidence, a **one-time research cost at adoption** — no scheduled re-audit. That does not freeze it: a material upstream change may trigger a re-audit, the trigger being an event rather than a calendar. Unmaintained upstream, a licence change, a maintainer handover. Surfacing such a change is #63's existing job, so the trigger needs no mechanism of its own — distinct from the two additions #63 does need for the fork, below.

**Repository count is unconstrained** — *"we can have as many repos as we want."* The three-peer framing describes the **distribution** graph, not a limit on what the author may own. This was the only premise that could have overturned the fork.

**Distribution of the recommended bucket is deferred** to [#96](https://github.com/eranroseman/knowledge-harness/issues/96). A README link is the interim position; a two-package split waits until the recommended list justifies one.

**`software-development`'s first function** is to be the single home for the non-as-is assets, managed in one place rather than per repository — hence rungs 3–5 default there.

## How assets can physically travel

**Measured.**

**Legality.** MIT throughout — `obra/superpowers` (© 2025 Jesse Vincent), `mattpocock/skills` (© 2026 Matt Pocock). The grant covers modified copies; the binding condition is that `software-development` and `sensemaking` each ship the notice and copyright line.

**Structure.** Anything shipping *inside* a plugin must be a vendored copy in that plugin's root. Three independent facts force it:

- [Agent Plugins](https://agent-plugins.org/specification) §4.1 requires every discovered file to resolve inside the plugin root; a `SKILL.md` that does not **must be skipped silently**.
- Codex copies the plugin tree and **drops symlinks**, so a symlinked skill arrives empty.
- `~/.codex/plugins/cache/superpowers-dev/superpowers/6.2.0/.codex-plugin/plugin.json` declares `"skills": "./skills/"` — a **single path string**, not an array. No subset can be curated from one path.

`mattpocock/skills` cooperates: `find . -type l` over the repo returns one symlink, `./AGENTS.md -> CLAUDE.md` at root, none inside `skills/`. Every skill folder is self-contained, so copying it in satisfies §4.1 with no rework.

**Consequence:** every vendored copy, modified or not, becomes a #63 drift surface. A dependency on a **separately distributed plugin** does not, keeping its own root. That asymmetry is why rung 2 outranks rung 3.

## Plugins

| Plugin | Harness | Rung | Bucket | Fork call |
|---|---|---|---|---|
| `superpowers` | both | **2 — fork plugin** | required | **fork** |
| `superpowers-developing-for-claude-code` | Claude | 4 — adapt its two skills | — | — |
| `obsidian` | both | 1 — plugin as-is | recommended | depend upstream |
| `writing-clearly-and-concisely` | both | 1 — plugin as-is | recommended | depend upstream (softaworks) |
| `diataxis-skills` | both | 1 — plugin as-is | recommended | depend upstream |
| `codex` (openai-codex bridge) | Claude | 1 — plugin as-is | recommended | depend upstream |
| `codex-security` | Codex | 1 — plugin as-is | recommended | depend upstream |
| `security-guidance` | Claude | 1 — plugin as-is | recommended | depend upstream |
| `ponytail` | both | 1 — plugin as-is | recommended | depend upstream |
| `caveman` | both | 1 — plugin as-is | recommended | depend upstream |

Four rows need reasoning; `superpowers` gets its own section.

**`caveman` — recommended (author, 2026-08-31), on use rather than on the necessity test.** Nothing in `software-development` invokes it, so the necessity test would have said `unrelated`; the author's reason is that it has earned its keep in practice. Two of four passes split on the call.

Note the deferral this carries. The argument that would make it `recommended` on the merits — its core mode is general compressed communication, and only `caveman-commit` and `caveman-review` are git-specific — is **domain-neutral**, which would put the dependency in the shared distributable rather than in `software-development`. Recommending it here instead is a decision to serve the current consumer and revisit if the vault ever wants it. That revisit is the trigger, and it is worth writing down as one rather than leaving implicit.

**`writing-clearly-and-concisely` — depend on softaworks, as installed.** Two premises from the original brief were wrong.

*Not a bundle.* `softaworks/agent-toolkit`'s `marketplace.json` offers **56 separate plugins**, each one capability. `enabledPlugins` carries `writing-clearly-and-concisely@agent-toolkit` and nothing else from the 56; the installed tree is one skill directory. The granularity a fork would buy is already upstream.

*And obra did not fork it — the derivation runs the other way.* `obra/the-elements-of-style` was created **2025-10-14**, `isFork: false`, no parent; `softaworks/agent-toolkit` **2026-01-19**, its skill first appearing 2026-01-18. obra predates it by three months, so a fork from softaworks is chronologically impossible. The two `SKILL.md` files are near-identical in authored wording — same "When to Use This Skill" list closing on the same bolded *"If you're writing sentences for a human to read, use this skill."*, same three-step "Limited Context Strategy" — which is copying, not parallel invention. So **softaworks derived from obra**, permitted by obra's `"license": "Public Domain"`. The Strunk text is public domain either way; the authored wrapper establishes direction.

*Keep softaworks, on content.* **Its split makes the skill's own strategy work** — both files tell the agent to dispatch a subagent with "the relevant section" under context pressure, and only softaworks can, its Strunk text being five files of 303 B to 33 KB. obra ships one 71 KB `elements-of-style.md` and warns it *"consumes ~12,000 tokens"*, describing a capability its layout does not support. And **`signs-of-ai-writing.md` has no counterpart** — 94 KB, larger than the Strunk text, covering what *not* to do. For a vault whose prose is substantially agent-drafted, that half plausibly outweighs the 1918 half. Totals: 178 KB against 73 KB. softaworks' description is also better shaped for invocation — *"Use when writing prose humans will read—"* is a trigger; obra's *"Apply Strunk's timeless writing rules to ANY prose"* is an instruction.

*The counterpoint.* softaworks last pushed 2026-03-05 against obra's 2026-08-12 — six months quiet. That matters little for a 1918 text, but `signs-of-ai-writing.md` decays, since AI writing tells change. **This is the plugin most likely to fire the re-audit trigger**, and the thing to watch is that file, not the commit rate.

*Before installing both:* obra's plugin is `elements-of-style` but its skill is also `writing-clearly-and-concisely` — no plugin collision, but identical skill names, which per #89 leaves two catalog entries with nothing to resolve them.

**`security-guidance` ships no skills, agents or commands** — hooks only: six registrations invoking a shared entrypoint over roughly 330 KB of interdependent Python across 9 modules, plus an Agent SDK bootstrap at SessionStart with a 180-second timeout. Its Stop-hook half has no Codex equivalent; Codex's event set is `pre_tool_use`, `post_tool_use`, `permission_request`, `pre_compact`, `post_compact`, `session_start`, `session_end`, `user_prompt_submit`, `subagent_start`, `subagent_stop` — no main-agent Stop. Rung 1 avoids vendoring that Python for a Claude-only capability `codex-security` already covers otherwise.

**`superpowers-developing-for-claude-code` has no bucket and no fork call: the plugin is not adopted.** Both its skills are rung-4 adaptations into `software-development` (see [The obra pair](#the-obra-pair)), so there is no dependency to bucket and nothing to fork. An earlier draft marked it `required` because the destination is a maintainer product; the bucket test asks whether `software-development` runs without it, and it does. *Why vendor rather than fork, since rung 2 outranks rung 3.* The plumbing is disproportionate: a fork means a repository, a marketplace registration, a Claude `dependencies` entry and a `codex plugin add` line in #62's setup — for **two skills** — and `software-development`'s first function is to be the single home for exactly these. The edits also differ in kind: the hardcoded paths are upstream defects a fork would fix naturally, but subordinating Phase 1 and Phase 6 to the superpowers spine is *our* opinion, which sits better as our own content than as permanent divergence in someone else's plugin.

*The counter is real and this is the closest call in the table.* Upstream is **dormant** — `pushedAt` 2025-12-03, main HEAD equal to the `v0.3.1` tag equal to the installed pin `74afe935`, nine months with no unreleased work — so a fork would never need merging, and merge burden is forking's main cost. A fork could also add the `.codex-plugin/` manifest the plugin lacks, making it installable on Codex as itself. **What flips it:** if these two skills should be first-class plugin content on Codex rather than reference material `software-development` ships, fork and add the manifest.

## superpowers — fork it

**Nature.** The author's position on as-is adoption is an observation, not a ruling — verbatim: *"I didn't rule that superpowers can't be adopted as-is. I said unfortunately the evidence suggests it is impossible."*

**Rung 1 fails — measured.** `hooks/hooks.json` registers a SessionStart hook on matcher `startup|clear|compact`; `hooks/session-start` injects `skills/using-superpowers/SKILL.md` verbatim inside `<EXTREMELY_IMPORTANT>` tags. That file routes to the skill being replaced, by qualified name, twice — line 22, *"**Before entering plan mode:** if you haven't already brainstormed, invoke the brainstorming skill first"*, and line 30, *"`\"Let's build X\"` → superpowers:brainstorming first, then implementation skills"*.

So the cost is not a passive catalog duplicate a better description could out-compete, but an always-on injected directive naming the competitor — and once inside, `brainstorming`'s `<HARD-GATE>` and its *"The ONLY skill you invoke after brainstorming is writing-plans"* clause foreclose handing back. The failure is not "picks arbitrarily"; it is "reliably picks the replaced skill, then locks the door."

**And it cannot be muted — measured against the binary** at `~/.local/share/claude/versions/2.1.220`:

```js
function jFe(e) {
  if ((e.type === "local-jsx" || e.type === "local") && sPy.has(e.name))
    return eo().skillOverrides?.[e.name] === "off" ? "off" : "on";
  if (e.type !== "prompt" || e.source === "plugin") return "on";
  let t = eo(), r = t.skillOverrides,
      n = r?.[e.name] ?? (e.unqualifiedName != null ? r?.[e.unqualifiedName] : void 0) ?? "on";
  ...
}
```

`e.source === "plugin"` returns `"on"` unconditionally; the override map is never reached. The branch above is not a plugin path — `sPy` is `new Set(["auto-mode-setup"])`, one built-in command. Corroborated twice in the same binary: `/skills` excludes entries where `loadedFrom !== "skills" && loadedFrom !== "commands_DEPRECATED"`, and `/plugin` exposes only `plugin:toggle` and `plugin:install`. Codex is more total, not less: `codex plugin --help` on codex-cli 0.147.0 lists only `add`, `list`, `marketplace`, `remove`; there is no `codex skill` subcommand and `~/.codex/config.toml` carries no skill-level key.

This settles #60's question, which was framed on borrowed authority: #60 cited research-vault's foundation specification (`docs/superpowers/specs/2026-08-16-foundation-spec.md`, §7), which governs **that** product and whose status note warns its contents *"should not be over generalized"*. `software-development` inherits no doctrine from it. The fact settles it, not the citation.

**Rung 3 — vendoring its components — fails too, measured.** The wanted skills carry **26** hard-coded `superpowers:`-qualified cross-references across 9 files, on 25 lines (one carries two), verified by `grep -ro` against the installed cache. **None sits inside `skills/brainstorming/`**, so every one survives that deletion and every one breaks under vendoring.

| File | Lines carrying a reference |
|---|---|
| `subagent-driven-development/SKILL.md` | 6 |
| `writing-plans/SKILL.md` | 4 |
| `writing-skills/SKILL.md` | 4 |
| `executing-plans/SKILL.md` | 3 |
| `systematic-debugging/SKILL.md` | 2 |
| `using-superpowers/SKILL.md` | 2 |
| `using-superpowers/references/gemini-tools.md` | 2 |
| `test-driven-development/writing-good-tests.md` | 1 |
| `writing-skills/testing-skills-with-subagents.md` | 1 |

Examples: `writing-plans/SKILL.md:163` — *"**REQUIRED SUB-SKILL:** Use superpowers:subagent-driven-development"*; `systematic-debugging/SKILL.md:177` — *"Use the `superpowers:test-driven-development` skill"*.

The breakage is permanent: 20 commits since 2026-01-01 touched `superpowers:` strings under `skills/`, `writing-skills/SKILL.md:283` prescribes the qualified form as house style, and such changes **auto-merge without conflict**, so each future one lands silently broken. Copying these skills out means editing 26 references, which is rung 4 by definition — specific to `superpowers`, since a byte-identical copy stays at rung 3.

**Rung 2 — fork — is the answer.** Qualified names are `pluginName:skillName`, independent of marketplace, corroborated live against `superpowers-developing-for-claude-code:developing-claude-code-plugins`, namespaced by plugin name while its marketplace is `superpowers-developing-for-claude-code-dev`. **Keeping `"name": "superpowers"` preserves all 26 references untouched.**

Measured by building the fork at pin `44c9b2d6` and merging upstream HEAD `b36e0829` (v6.3.0, five weeks, 415 lines):

- Patch: **10 files changed, 117 insertions, 1933 deletions** — delete `skills/brainstorming/`, edit two lines of `using-superpowers/SKILL.md`, replace the `AGENTS.md` symlink with a regular file.
- Merge: **exactly two conflicts**, both `DU` on the deleted directory, resolved by `git rm -r`, fully scriptable.
- The one file the fork edits **auto-merged cleanly** even though upstream touched it.

**Upstream health.** `obra` (Jesse Vincent), 279,648 stars, last push 2026-08-29, monthly releases (v6.1.0 06-30, v6.2.0 07-24, v6.3.0 08-12), 100 commits touching `skills/` since 2026-06-01. No `eranroseman` fork exists. **The machine is pinned at 6.2.0 while v6.3.0 shipped 2026-08-12** — one minor behind, that delta touching 13 skill files across 7 skills.

**Asking upstream is a non-starter.** `brainstorming` is the plugin's first manifest keyword and its `defaultPrompt` is *"I've got an idea for something I'd like to build."* — the front door obra is selling.

**A fourth arrangement, rejected.** Claude Code marketplace entries can declare a plugin's components — the binary carries *"has conflicting manifests: both plugin.json and marketplace entry specify components. Set `strict: true` in marketplace entry or remove component specs from one location."* Since upstream's `.claude-plugin/plugin.json` declares no components, an entry-level `skills` array selecting 13 of 14 would conflict with nothing: curation with no fork and no vendoring. **It dies on Codex**, whose single-path `skills` key cannot express a subset.

**Three live defects a fork lets you fix — each by a different act.**

| Defect | Fixed by |
|---|---|
| Codex's `[marketplaces.superpowers-dev]` is `source_type = "local"`, pointing into `~/.claude/plugins/marketplaces/`, so the Codex install is parasitic on a Claude install happening first and **cannot reproduce on a fresh machine**. Every other Codex marketplace here is `source_type = "git"`. | Publishing the fork at a **git URL** |
| #56's missing Codex `AGENTS.md`: `git ls-files -s AGENTS.md` returns mode `120000` (a tracked symlink) while `git status --porcelain` reports ` D AGENTS.md` and no file exists. Codex drops the symlink, so 8,873 bytes of plugin-level guidance are silently absent. | The **10-file patch**, which commits it as a regular file |
| Codex's manifest declares `"hooks": {}`, so **superpowers' SessionStart hook does not fire on Codex at all**, though `hooks/` is copied there. Codex supports `session_start` and sets `CLAUDE_PLUGIN_ROOT`; superpowers does not wire it. | **Nothing yet.** The measured patch does not wire it either — a fork makes the fix *possible*. Route to #61 |

**Known gaps.** The patch is under-scoped as measured: `tests/brainstorm-server/` holds 12 live test files hard-coding `skills/brainstorming/scripts/...`, all orphaned by the deletion. And a fork nobody merges becomes a stale private snapshot — the failure `harness-backup` exists to avoid, reintroduced elsewhere. **Without #63's merge-base monitor the fork is strictly worse than rung 1**, making that monitor a precondition rather than an enhancement.

**This reverses a clause of [#72](https://github.com/eranroseman/knowledge-harness/issues/72)**, which recorded the process spine as "adopted as-is" while vendoring `brainstorming` out of it — two statements that cannot both hold at plugin granularity. Recorded as a dated reversal per the precedent [#77](https://github.com/eranroseman/knowledge-harness/issues/77) set over [#89](https://github.com/eranroseman/knowledge-harness/issues/89). Everything else in #72 stands; **only the adoption mechanism changes.** The reversal is this ticket's, drawn from the measurements above — not an author ruling.

## mattpocock's skills — 18 installed

Standalone via `~/.agents/.skill-lock.json`, not as a plugin. All adopted skills are **rung 3, vendored** into whichever product needs them.

- **To `sensemaking`:** `grilling`, `research`, `handoff`, `teach`, `to-questionnaire`, `wait-what`, `wayfinder`, `wizard`, `writing-for-agents`.
- **To `software-development`:** `codebase-design`, `prototype`, `resolving-merge-conflicts`, `improve-codebase-architecture`, `triage`, `domain-modeling`, `grill-with-docs`.
- **Rung 4, adapt:** `setup-matt-pocock-skills`, into `software-development` — the template for #62's setup mechanism rather than a shipped capability, so the sharing axis does not apply.
- **Not adopted:** `to-tickets`, per #72's process-skill ruling.

Six were independently hash-matched against exact upstream commits and are **pristine but stale** — `domain-modeling` @ `54bc6b6`, `triage` @ `6a34259e`, `writing-for-agents` @ `4aaccb58`, `setup-matt-pocock-skills` @ `c66bdee`, `grilling` @ `86cba45f`, `wayfinder` @ `6a34259e`.

**`domain-modeling` is `software-development` only, and the reasoning that nearly made it shared was wrong.** An earlier pass argued the call graph forced it: `wayfinder` is shared and invokes it unconditionally twice — the default ticket type (*"Always call the Skill tool twice"*, `wayfinder/SKILL.md:79`) and the mandatory first act of charting a map (*"Name the destination"*, `:111`) — with a third, conditional call at `:124` (*"If in doubt"*). A research-vault-only install leaves those dangling.

That test optimised for closing the call graph rather than for the right outcome, never weighed presence against absence, and counted one of three callers.

*The caller map argues the other way.* Three skills call `domain-modeling`: `wayfinder` (`sensemaking`), `triage` (`software-development`, `:76`) and `improve-codebase-architecture` (`software-development`, `:66`). Assigning it to `software-development` satisfies **two of three**; `sensemaking` satisfies one. The whole graph points where the content already pointed.

*Presence is not neutral.* The skill is repo-shaped: its description reads *"Use when discussing **codebase** terminology, writing or editing a **CONTEXT.md**, or recording or editing an **ADR**"*; its structure section opens *"Most **repos** have a single context"* and diagrams `src/`, `docs/adr/`, `CONTEXT.md`; it carries a *"Cross-reference with code"* step and ships `ADR-FORMAT.md` and `CONTEXT-FORMAT.md`. A scaffolded vault has none of those — `templates/`, what `setup-vault` ships, contains neither `CONTEXT.md` nor `docs/adr/`. And the skill creates what it does not find: *"If no `CONTEXT.md` exists, create one when the first term is resolved. If no `docs/adr/` exists, create it when the first ADR is needed."* A shared `wayfinder` invoking it in a vault session would write code-project scaffolding into an OKF-conformant vault — damage, not clutter.

*Absence costs a retry.* The Skill tool errors, the agent proceeds, and no domain modelling happens — correct where the discipline does not apply.

*Rung 3, not 4.* Earlier passes put it at rung 4 with "resolve the split" as its adaptation. The split is resolved, the copy is hash-matched pristine, no other adaptation was named — so it vendors unmodified and leaves #60's list.

Two ways to remove the dangling `wayfinder` call if it irritates in practice, neither taken: adapt `wayfinder` so its grilling ticket type does not invoke `domain-modeling` unconditionally, moving `wayfinder` to rung 4 and buying a permanent adaptation; or leave it, the error being visible to the agent and costing one retry.

**`grill-with-docs` is adopted, reversing #72 for this skill (author, 2026-08-30).** #72 dropped it with mattpocock's other process skills after #85 found it has no interview logic of its own — its whole body is *"Call the Skill tool twice, for `grilling` and `domain-modeling`."* Seven lines, `disable-model-invocation: true`, shipping `agents/` for Codex.

Two things make it worth keeping. It is a **user-typed composition**, not a competing entry point — being outside the model catalog, it cannot race the spine, which is what #72's process-skill ruling was guarding against. And **both callees resolve in `software-development`**: `domain-modeling` lives there, `grilling` arrives via `sensemaking`. It vendors unmodified at rung 3; the bare names need no rewriting.

It is not the `rethink` case. `rethink` restated a line already inside `rethink-audit`; `grill-with-docs` composes two skills, neither of which contains the composition — the same pairing `wayfinder:79` reaches for by hand.

**`resolving-merge-conflicts` fills a second spine gap, and more cheaply than `diagnosing-bugs` fills the first.** `finishing-a-development-branch` contains **zero occurrences of "conflict"**. Its Option 1 runs `git checkout <base-branch>`, `git pull`, `git merge <feature-branch>`, then goes straight to verifying tests — handling *tests failing after a successful merge* (*"stop, leave the worktree and branch in place, and investigate"*) but saying nothing about either command conflicting. The spine instructs an agent to run a merge and is silent on the most common way it goes wrong, at the moment the tree is dirty and mid-operation.

`resolving-merge-conflicts` is exactly that path — *"Use when you need to resolve an **in-progress** git merge/rebase conflict"*. The integration is one conditional after the merge step in the fork's `finishing-a-development-branch/SKILL.md` — attached to **Option 1 (merge locally)** specifically, since Option 2 defers conflicts to the forge. It is cheaper than the debugging case on every axis: **no trigger race** (the description is situational, firing only when a conflict already exists, so no muting is needed), no classifier, and the skill stays **rung 3, vendored unmodified**.

**`prototype` is the same shape and answer.** `wayfinder` calls it at one site, reached only when a prototype ticket is created. Its absence degrades `wayfinder` to three ticket types, and a researcher plausibly never reaches for *"a throwaway prototype... UI/logic code"*.

**Why not fork `mattpocock/skills`, given rung 2 outranks rung 3?** Four reasons, the first decisive.

- **Forking buys nothing here.** What carries the `superpowers` fork specifically is namespace preservation, and that does not apply: `grep -ro 'mattpocock-skills:'` across the installed set returns **zero**. Every cross-reference is a bare name — `grilling` referenced by `improve-codebase-architecture`, `triage` and `wayfinder`; `domain-modeling` by three; `prototype` by two — and bare names survive relocation.
- **Two forks would collide on the name.** The adopted skills split across two distributables, so one fork cannot serve both, and two cannot both be `mattpocock-skills`. One must be renamed, paying for a namespace benefit that does not exist.
- **Doubled merge burden on a live upstream**, each fork maintaining a different deletion set indefinitely.
- **Recategorisation becomes a two-repository transaction** — a delete in one fork and an add in the other, in lockstep, where vendoring makes it a file move.


## mattpocock's skills — 19 not installed

**Scope caveat.** #75's declared inventory sources are what is *installed*. These nineteen were surveyed at the author's request for completeness, so they sit outside the ticket's scope and their verdicts carry less authority — a reading of upstream, not a disposition of an installed asset.

The upstream roster is 37 skills — engineering 18, productivity 7, in-progress 8, misc 4 — certified by mechanical set-diff against `find skills -name SKILL.md`, empty both directions.

**Fifteen are recommended not adopted:** `ask-matt`, `code-review`, `implement`, `tdd`, `to-spec`, `grill-me`, `claude-handoff`, `implement-spec`, `loop-me`, `retro`, `setup-ts-deep-modules`, `git-guardrails-claude-code`, `migrate-to-shoehorn`, `scaffold-exercises`, `setup-pre-commit`. Adopting something the author lives without required naming a concrete gap it fills; none did. The only dissent ran the other way: two of four passes argued `tdd` and the `writing-*` trio were declined without pricing an adaptation.

**Four were parked, not declined, and the survey could not say so.** The standing recommendations register (`docs/product-landscape/2026-08-25-coding-companion-plugins-comparison.md`) parks each with an explicit trigger; it was not supplied to the assessment passes, which is why they missed this. Before the `defer` state existed, a parked skill was indistinguishable from a rejected one.

| Skill | Register's trigger | Correct state |
|---|---|---|
| `diagnosing-bugs` | *"evaluate at the next real debugging need"* (register item 09) | **adopt now, rung 4** |
| `writing-fragments` | *"serious candidates for workload 3's map"* | defer to workload 3 |
| `writing-beats` | same | defer to workload 3 |
| `writing-shape` | same | defer to workload 3 |

Adopted at workload 3, the writing suite lands at **rung 3 with a vendored snapshot**, because upstream marks all three in-progress — *"can change or disappear"*.

**`diagnosing-bugs` is a correction rather than a deferral: adopt at rung 4, hard-gated to explicit invocation.** Both decline reasons were true only of as-is adoption. *The Codex miscalibration is real* — upstream documents it over-firing on non-Claude models, four reports on issue #578 — *and the fix is the vendor's own prescription*: `policy:\n  allow_implicit_invocation: false` in `agents/openai.yaml`. Two lines, and upstream's house convention rather than a workaround — **22 of its skills carry it**, including `ask-matt`, `implement`, `grill-with-docs`, `wayfinder`, `triage` and `teach`. *The trigger race with `superpowers:systematic-debugging`* is resolved by the same gating plus a Claude-side `user-invocable-only` override while the skill remains lockfile-installed.

The register backs it with the strongest evidence in this survey — not an opinion but **an audited failure of this repository's own work**, validation item 5: *"the run's most expensive error class (instrument scope — the `.pop()` measurement missing `{\"date-parts\": []}`) maps onto its Phase-1 red-capable-loop criterion; systematic-debugging has no equivalent."*

Reading both skills confirms it, and it is worse than a missing feature. **On the one point where they overlap the spine is inverted**: `systematic-debugging`'s Iron Law gates *fixes* on investigation; `diagnosing-bugs` gates *investigation* on a red-capable command existing. The spine carries no loop-construction material anywhere — not in `SKILL.md`, `root-cause-tracing.md`, `defense-in-depth.md` or `condition-based-waiting.md`.

The register recommends **coexistence, not substitution** — item 09 reads *"diagnosing-bugs **beside** systematic-debugging"*. Its looser win-section line calls loop-first *"arguably a better fit for this repo's measurement doctrine than systematic-debugging's four phases"*, but that compares approaches rather than proposing a removal.

**Replacement was costed and is UNSAFE.** A two-directional comparison read every file in both skills, each direction adversarially verified. Both directions reached the same verdict independently.

*The decisive reason is a contradiction, not a gap.* The adoption plan gates `diagnosing-bugs` to explicit invocation. The slot replacement would vacate is `using-superpowers/SKILL.md:31` — *"'Fix this bug' → superpowers:systematic-debugging first"* — a line whose entire function is to fire **implicitly** on a free-form bug report. A skill hard-gated to explicit invocation cannot occupy a routing line defined by implicit firing. Either the gate goes, reproducing upstream's most-reported defect, or the slot goes unfilled and every "Fix this bug" routes nowhere. **Hard-gating and replacement are mutually inconsistent, so the gate entails coexistence.**

*And the two skills claim different ground by their own text.* `diagnosing-bugs` opens *"A discipline for hard bugs"*, and its essay adds *"It is heavy by design, and the wrong tool for a question you want answered in one message."* `systematic-debugging` claims exactly that territory — *"Don't skip when: Issue seems simple (simple bugs have root causes too)"* — with a proportionate cheap-first Phase 1. Replacement would leave routine bugs with no home.

*The spine also carries four things `diagnosing-bugs` does not address at all*, confirmed by grep over its whole directory: the fix-at-source mandate (`root.cause`, 0 hits), backward call-chain tracing with stack instrumentation (`stack`, 0 hits), defense-in-depth validation (`defense`/`validate`, 0 hits each), and test-pollution bisection. The vendor concedes the first himself: *"There is no gate between instrumentation and the fix, so the agent can start writing code before you have agreed with its root cause."*

*Which settles a narrower question too:* `diagnosing-bugs` is **not** a replacement for `root-cause-tracing.md`. They cover disjoint branches of a decision the spine already documents — `root-cause-tracing`'s own graph routes *"Can trace backwards? → no — dead end → Fix at symptom point"*, contradicting its own closing rule. That dead end is where a loop-and-hypothesise method starts, which is what makes the carry-across below the right shape rather than merely a cheap one.

**Five ways to get the method in, costed.** The fork owns `skills/systematic-debugging/`, and that `SKILL.md` is quiet — untouched between the pin and HEAD, 3 commits since 2026-01-01, none since 2026-07-05 — so editing it is cheap.

| | Shape | Cost |
|---|---|---|
| A | Adopt `diagnosing-bugs`, rung 4, hard-gated to explicit invocation | Never reaches the implicit path; `root-cause-tracing`'s dead end stays broken |
| B | Carry `building-a-feedback-loop.md` into the spine's Supporting Techniques | Advisory only — cannot carry the Phase-1 gate or the ranked-hypotheses ordering, both *not-separable* |
| C | Edit the gate and hypothesis discipline into the spine's phases | Dissolves B's objection, but you hold a snapshot and forfeit upstream improvements |
| D | Vendor `diagnosing-bugs` with a non-triggering description, and repoint `root-cause-tracing`'s dead-end edge at it | Smallest patch; the gate stays intact inside its own skill and upstream keeps flowing. Routes only *after* tracing has failed |
| **E** | **Restructure the spine's entry as a three-path classifier, third path invoking `diagnosing-bugs`** | **Recommended** |

**E, on upstream's own pattern.** v6.3.0 rebuilt `brainstorming` as a Spike / Bounded / Architectural router: classify before the first question and say it aloud, entry criteria that test the artefact rather than the agent's confidence (*"Bounded measures the repo, not your familiarity"*), path-bound terminal states, per-path checklists, and mandatory re-classification mid-task (*"Hidden complexity upgrades the path mid-task. Stop and say so"*). Ceremony scales with the task; the gate never does.

Debugging takes the same shape — **simple** (error and recent diff explain it; the spine's existing cheap Phase 1), **traceable** (a call chain to walk; `root-cause-tracing.md`), **opaque** (no chain, or non-deterministic; `diagnosing-bugs`). That makes explicit a split both skills already assert against each other: the spine claims *"simple bugs have root causes too"* while `diagnosing-bugs` calls itself *"heavy by design, the wrong tool for a question you want answered in one message."*

E beats D because classification happens **before** the tracing attempt rather than after it fails, and it has an argument no other option has: **it is the shape upstream just moved to.** If obra restructures `systematic-debugging` as he restructured `brainstorming`, a fork already shaped that way diverges less.

Under D or E, `diagnosing-bugs` is vendored with a description that describes rather than triggers — the over-firing upstream documents is a description-match defect, so removing the trigger text removes it. Do not reach for `skillOverrides`: a vendored skill is a plugin skill, which overrides cannot touch, and Codex has no equivalent. Owning the frontmatter makes the point moot.

**E's own risk:** misclassification is a failure mode the current spine does not have. Upstream mitigates it with an anti-pattern table, which is copyable in form.

**One register recommendation is stale.** It proposes *"de-fanging the injection selectively in settings (`skillOverrides` name-only, the grilling precedent) gets nearly all the benefit at none of the fork cost."* It does not work, and the diagnosis is precise: **`grilling` is lockfile-installed, where `skillOverrides` does reach.** The register generalised that precedent to plugin skills, where the resolver returns `"on"` before consulting the override map.

## The obra pair

`working-with-claude-code` and `developing-claude-code-plugins` are each installed **twice** — inside the `superpowers-developing-for-claude-code` plugin, and standalone via the lockfile from the same upstream.

**Both are rung 4, both to `software-development`, neither shared.** They separate on *consumer* rather than depth: `developing-claude-code-plugins` is an authoring workflow whose artefacts are `.claude-plugin/plugin.json`, `marketplace.json`, `hooks.json` and git tags; `working-with-claude-code` is a runtime reference whose nine "When to Use" triggers are all harness extension, configuration and troubleshooting. A researcher produces neither.

**What forces rung 4, and decides the dedupe: each install is broken in a way the other masks.**

- The **plugin's** `working-with-claude-code` hardcodes standalone paths — `SKILL.md:119` reads `path: ~/.claude/skills/working-with-claude-code/references/`, `SKILL.md:132` invokes `node ~/.claude/skills/working-with-claude-code/scripts/update_docs.js`, and `${CLAUDE_PLUGIN_ROOT}` appears **zero** times. Neither resolves from a plugin install; they resolve today only because the standalone copy exists.
- The **standalone** `developing-claude-code-plugins` references `examples/simple-greeter-plugin/` and `examples/full-featured-plugin/` in three places, but those live at **plugin root**. The lockfile install ships no examples at all.

**So the dedupe is: keep both now, drop both later.** An earlier draft recommended keeping the plugin and dropping the lockfile entries; that is wrong on this evidence, since removing either copy today breaks the other. `software-development` ships the adapted copies first, at which point both installs become redundant together. **The adaptation is what makes deduplication safe, not a precondition of it.** Routes to #60 and #62 as one motion.

**A drift asymmetry for #63.** `working-with-claude-code`'s true upstream is not obra: its 42 reference files are generated from `docs.claude.com` by the bundled `scripts/update_docs.js`, and they are stale — missing `skillOverrides`, plugin `dependencies`, and `allowCrossMarketplaceDependenciesOn`, all three of which this programme relies on. Its drift question is "have Anthropic's docs moved", not "has obra committed", so a monitor watching the obra pin reports clean while the content rots.

## The four harness-backup skills

Recommendation only — the owning tickets decide.

| Skill | Rung | Home | Owning ticket |
|---|---|---|---|
| `consistency-audit` | 3 — vendor | `software-development` | #79 |
| `rethink-audit` | 4 — adapt | **`sensemaking`** | #73 |
| `rethink` | **not adopted — drop** | — | #73 |
| `finding-duplicate-functions` | 4 — adapt | `software-development` | #60 |

**`consistency-audit` is `software-development`, after two reversals.** The original pass said so from framing vocabulary (*"read a **repository** whole"*); a second reversed it to `sensemaking` on capability, since *"contradictions, duplication, drifted terms, stale claims"* is what a research vault accumulates. Both were reasoning from the description. Reading the skill settles it: **the capability transfers and the plumbing does not.**

Two blockers, neither cosmetic. Its report destination is hardcoded — *"Write the report to `docs/superpowers/specs/YYYY-MM-DD-<scope>-audit.md`"* (`SKILL.md:201`), a path no vault has. And its terminal state is `"Invoke writing-plans skill"`, the doublecircle in its After-the-Audit graph — a superpowers skill, `software-development`-only, so on a vault the audit's *exit* calls something absent.

The mismatch is structural rather than a path string. A vault already has a destination for adjudicated findings: the foundation spec routes them to `inbox/review-queue.md` as append-only entries carrying reason codes and human acknowledgment. A vault audit should terminate there, not in a plan. A skill needing a different exit shape per product is two skills sharing a method, not one shared skill — which is what a survey pass meant in flagging a vault-side `vault-audit`/`tangle-check` derivative for #79 or the research-vault roster.

Its subagent travels either way. `consistency-audit` hard-dispatches `consistency-audit-inspector` at `SKILL.md:78` (*"two independent readers over every slice"*) and `:116` (*"instructed to refute"*), and that agent lives outside the skill directory at `~/harness-backup/claude/agents/`. #51 flagged it as outside the drift detector's watched set and deferred it to #78 — still open, and more load-bearing once the agent ships rather than sitting local.

**`rethink` is dropped, on duplication rather than principle.** Its entire body is one sentence: *"Run a `/rethink-audit` pass on a fresh design question: no implementation exists, so work through `design:` and finish at `trade-offs:`."* `rethink-audit` already carries that at line 60: *"On a fresh design question there is no implementation: run through `design:`, then `trade-offs:`."* Near-verbatim — not a wrapper adding a parameterisation but a restatement of a line inside the skill it delegates to.

This answers #73's second question differently from how that ticket frames it: the front door does not absorb `/rethink` and it does not survive as a distinct entry point — **`rethink-audit` absorbed it already.** It also means `rethink-audit` needs no adaptation for the fresh-design case, keeping it at rung 3.

**`rethink-audit` is `sensemaking` at rung 4 — the mirror image of `consistency-audit`.** Same family, opposite answer, and the same check separates them: its plumbing is clean where the other's is not.

- **No hardcoded write path.** *"Lists findings, applies nothing. One-shot."* The `docs/research/rethink-audits/` convention belongs to this repo, not the skill.
- **No mandatory exit into an absent skill.** `SKILL.md:38` reads *"Run the `codebase-design` skill, **if available**"* — explicit optional composition. `superpowers:writing-plans` appears only as a note that `migrate:` is *"the input `superpowers:writing-plans` wants"*; `superpowers:brainstorming` only under Boundaries. Pointers, not invocations.
- **It writes nothing**, so the harm test that decided `domain-modeling` does not apply. Worst case on a vault is confusing guidance, not scaffolding written into an OKF bundle.

Its skeleton — `requires:` → `prior-art:` → `design:` → `gap:` → `trade-offs:` → `migrate:` — is domain-neutral. Roughly 8 of 87 lines carry code vocabulary: *"signatures, call sites, tests"* (`:19`), the evidence tags `caller`/`tests`/`docs`/`adr`/`assumed` (`:22`), *"Read the current implementation"* (`:46`). Examples and tags, not method. And it already stretches: four of the seven audits in `docs/research/rethink-audits/` are not code — `controller-protocol`, `development-process`, `glossary-and-adr-triage`, `coding-companion-plugin-layering`.

**Rung 4, for #60:** generalise the boundary-reconstruction line and give the evidence tags vault equivalents. Both skills ship `agents/openai.yaml`, so they are cross-harness ready.

The *"if available"* at `:38` reads as a portability affordance but is not one. An agent that cannot find a skill does not invoke it, so the branch is redundant either way — which is why research-vault's doctrine bans the construction as dead text rather than as a hazard. What actually makes this skill portable is that `codebase-design` is optional to its method at all; the hedge is words, not mechanism.

The author has separately ruled that `rethink`/`rethink-audit` land in either `software-development` or `sensemaking`, and that **both** the public `eranroseman/rethink` repository and the harness-backup copies are deleted. Recorded on #73.

## The six sharing verdicts this ticket owed

Four deferred here by #89 — `domain-modeling`, `triage`, `writing-for-agents`, `setup-matt-pocock-skills`. Two left unforced — `working-with-claude-code` and `superpowers`. All six rest on skill bodies rather than folder names.

| Skill | Verdict |
|---|---|
| `writing-for-agents` | `sensemaking` |
| `domain-modeling` | **`software-development`** — repo-shaped (CONTEXT.md, ADRs, cross-reference with code), and it *creates* those artefacts where absent, so shipping it to a vault is damage rather than clutter. `wayfinder`'s call dangling on a vault-only install is the correct outcome |
| `triage` | `software-development` |
| `working-with-claude-code` | `software-development` |
| `superpowers` | `software-development` — meaning **`software-development` depends on it and `research-vault` does not**. The fork stays a separate plugin with its own root; this axis assigns which product needs the capability, not where files sit |
| `setup-matt-pocock-skills` | **the axis does not apply** — a rung-4 template feeding #62's setup mechanism, not a capability either product ships |

`working-with-claude-code` is the one reversal. It was argued during the grilling as shared, on the grounds that it documents the runtime both products run on; two passes placed it with engineering for the reasons under [The obra pair](#the-obra-pair).

## Handoff to #60

Every asset landing on rung 4. All six need a provenance header; the table lists what is needed beyond that.

| Asset | What must change |
|---|---|
| `brainstorming` → `writing-specs` | Rename; correct the description, which promises open-ended ideation while the body is a one-way funnel from idea to committed spec with a mandatory approval gate; decide the Visual Companion; decide the base version |
| `setup-matt-pocock-skills` | Adapt as the template for #62's setup mechanism, per #85 |
| `working-with-claude-code` | Rewrite the two hardcoded paths to `${CLAUDE_PLUGIN_ROOT}`-relative form; re-run `update_docs.js` to refresh the 42 references |
| `developing-claude-code-plugins` | Co-locate or re-path the two `examples/` directories; subordinate Phase 1 (Plan) and Phase 6 (Release) to `superpowers:writing-plans` and `superpowers:finishing-a-development-branch` so #72's spine is not duplicated |
| `finding-duplicate-functions` | Provenance header against `obra/superpowers-lab`; the local copy is a substantial rewrite, shell replaced with Python |
| `diagnosing-bugs` | Add `policy:\n  allow_implicit_invocation: false` to `agents/openai.yaml`; gate Claude-side invocation |

**The list shrank because of the fork.** Earlier passes marked `systematic-debugging`, `test-driven-development`, `writing-plans`, `writing-skills` and `using-superpowers` as rung-4 adaptations — artefacts of the vendoring branch, since a fork keeps the namespace. `using-superpowers` is still edited, but inside the fork as two lines of its ten-file patch, which is the fork's business rather than #60's.

**Two decisions #60 must make knowingly.**

*The Visual Companion is separable but not free.* 1,730 lines — `scripts/server.cjs` 723, `scripts/frame-template.html` 213, `scripts/start-server.sh` 209, `scripts/helper.js` 167, `scripts/stop-server.sh` 120, plus `visual-companion.md` 298 — within a `brainstorming` directory totalling 1,930 lines across 8 files. Nothing outside references it, so dropping it costs one file deletion, one directory deletion and about 19 lines from the body. But removing those 19 lines means *"internals untouched"*, which is what #72 specified, no longer describes the vendoring. The companion also loads a logo from an external site carrying the Superpowers version, opt-out via `SUPERPOWERS_DISABLE_TELEMETRY`.

*The base version matters.* Upstream HEAD replaced `brainstorming` with a three-path Spike/Bounded/Architectural router — 117 changed lines — **after** the 6.2.0 text #72 judged. Vendoring from the pin ships a skill already a generation behind. Vendor from HEAD, freeze deliberately, or place `writing-specs` under #63's drift watch as a tracked adaptation.

## Handoff to other tickets

**#62 — hard sequencing, and a migration.** The fork's edited bootstrap points at `software-development:writing-specs`. Until that ships, every session injects a route, inside `<EXTREMELY_IMPORTANT>` tags, to a skill that does not exist, so `writing-specs` must land before or with the cutover. The cutover must also uninstall first on both harnesses, since the fork keeps the plugin name and collides with the installed copy. **Two installs must be migrated, not one:** `installed_plugins.json` carries a project-scope entry for `/home/eranr/memoria-vault` at `gitCommitSha` `3dcbd5c4…` while the user-scope entry has `44c9b2d6…`, both naming the **same** `installPath`. Easy to miss, and it establishes that install path does not imply pin — which #63 and #78 should know independently.

**#63 — two additions.** Watch upstream HEAD against the fork's merge-base, not just the fork against the installed cache — a precondition, as the fork section states. And catch **unqualified** references: upstream already added `skill_view("brainstorming")` to `using-superpowers/references/hermes-tools.md:31`, which auto-merges clean and is invisible to a `grep superpowers:brainstorming`.

**#61 — a live constraint, not a blank slate.** A SessionStart injection already fires every startup/clear/compact from the forked superpowers, carrying the skill-invocation discipline. #61 must decide whether `software-development`'s own hook composes with that or duplicates it; Claude Code merges hooks from multiple plugins without dedup. The two edited routing lines in `using-superpowers/SKILL.md` are a supported seam and merge cleanly.

**#64 — two.** The declared-asset policy gap (below), and **`finding-duplicate-functions` is absent from `harness-backup`'s README entirely**, so a fresh-machine restore silently omits it.

**#81 — `to-spec` is mattpocock's PRD skill, renamed.** `CHANGELOG.md:181` — *"`to-prd` is renamed to `to-spec`"*; `docs/engineering/to-spec.md:38` — *"Where did `/to-prd` go? It is this skill, renamed in v1.1."* So #81's premise that no vendor's roster contains one is wrong in letter. It is worth more as a cited failure mode than as a donor, because upstream documents its own defect at `docs/engineering/to-spec.md:57`: *"The template leans hard on user stories, which is the wrong shape for architectural work: you end up writing stories nobody asked for around decisions that are really about interfaces and invariants."* Its template divides along exactly the line #81 must draw — product: Problem Statement, Solution, User Stories; engineering: Implementation Decisions, Testing Decisions; shared: Out of Scope, Further Notes. Also minable: `triage/AGENT-BRIEF.md`, 207 lines, MIT, already installed.

**#59 and #69 — a working cross-harness exemplar.** `obra/the-elements-of-style` carries generated manifests for eight harnesses in one repository — `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.devin-plugin/`, `.hermes-plugin/`, `.kimi-plugin/`, `.opencode/`, `.pi/`, plus `.agents/plugins/marketplace.json` — produced and checksummed by a tool, recorded in `.everyharness/manifest.json` as `"tool": "everyharness@0.7.0"`. A live answer to the question #59 asks about serving two harnesses from one source, bearing on #69's conformance check. Worth reading before either invents a layout.

**#78 — an offered requirement.** See anomaly 1.

## The five anomalies #75 carried

1. **The orphaned-cache count in the ticket body is wrong.** Of 16 directories under `~/.claude/plugins/cache/`, nine are enabled pins. Of the remaining seven: three are superseded versions of still-enabled plugins (garbage-collection lag from a batch update on 2026-08-10); three are **true orphans** with no enabled successor — `interface-design`, `pr-review-toolkit`, `frontend-design`, where the ticket named only the first; and one, `caveman/caveman/17f9f2ec2377`, is unreferenced **and unmarked**, with a larger roster than the pin. Filed as [#95](https://github.com/eranroseman/knowledge-harness/issues/95) and ruled out of scope for map #53 as machine hygiene.

   *The finding for #78:* the client's own `.orphaned_at` marker is **not** a complete signal — six of seven carry it and one does not — so a doctor check trusting it misses exactly the case most warranting a human look. Set subtraction against `installPath` is the reliable test. Offered as an inherited requirement, to take or decline.

2. **The double-installed obra skills** — decided under [The obra pair](#the-obra-pair).

3. **The dormant `rethink` marketplace** routes to #73 as one motion with the placement and deletion calls, per #51's deliberate bundling — deleting the upstream repository makes the registration dead by definition.

4. **The empty `claude-plugins-official` marketplace** is out of scope, filed with #95. It is a different registration from `claude-code-plugins`, which supplies the live `security-guidance` and must not be removed alongside it.

5. **The declared-asset policy gap was mislocated in the ticket body.** Not in this repository's `AGENTS.md`; it lives in the global `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`, both covering only the `npx skills add -g` path with no declared-asset surface for native installs. Routed to #64 by the author, on the reasoning that a hand-maintained table is the weakest tier under this repo's *eliminate > mechanism > rule > prose* ordering and goes stale on the next install.

## Appendix: method

Four adversarially-verified survey passes, plus a fifth cross-checking them against the standing recommendations register. Each assessed on evidence read off disk or fetched from upstream, then was refuted by an independent agent instructed to default to rejection where a claim rested on a description rather than a file body. Where the text above cites "two of four passes", that is the denominator.

Sources read fresh rather than inherited from earlier tickets: `~/.claude/settings.json`, `~/.claude/plugins/installed_plugins.json`, `~/.claude/plugins/known_marketplaces.json`, `~/.claude/plugins/cache/`, `~/.codex/config.toml`, `~/.codex/plugins/cache/`, `~/.agents/.skill-lock.json`, `~/harness-backup/claude/skills/`, and the installed Claude Code binary at `~/.local/share/claude/versions/2.1.220`.

Where a claim decided a branch it was re-verified by hand outside the surveys — the override resolver, the cross-reference count, the upstream licence and repository statistics, the Codex manifest, and the `writing-clearly-and-concisely` derivation chronology. Four reported figures were corrected that way: the cross-reference count (24 and 25 were both reported; 26 is correct), the upstream licence (`gh repo view` reported none; the licence endpoint confirms MIT), the orphaned-cache count, and the obra/softaworks derivation, inherited from the ticket brief as a fork by obra from softaworks and found to be neither a fork nor in that direction.

**One methodological failure worth recording**, because it produced four wrong verdicts rather than one: the standing recommendations register was never supplied to the four assessment passes, so the nineteen not-installed skills were judged without the repository's own prior evidence about them. The fifth pass exists only because that was noticed afterwards.
