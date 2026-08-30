# Installed asset disposition survey

**Status: recommendation. Nothing here is approved.**
**Date:** 2026-08-30 · **Ticket:** [#75](https://github.com/eranroseman/knowledge-harness/issues/75), a `wayfinder:grilling` ticket on map [#53](https://github.com/eranroseman/knowledge-harness/issues/53)

Every plugin and skill installed on this machine across Claude Code and Codex, plus the full upstream `mattpocock/skills` roster including the nineteen not installed here, and the four `harness-backup`-owned skills. Each gets a ladder rung, a bucket where one applies, a sharing verdict, and — for plugins — a fork call.

Companion to the [2026-08-28 alteration-inventory sweep](2026-08-28-alteration-inventory-sweep.md), which asked whether assets had drifted. This one asks what to do with them.

**The destination**, as map #53 states it and as several judgements below appeal to: an installable cross-harness plugin that is the canonical home for shared authored and deliberately adapted guidance and automation, running on **both Claude Code and Codex**, **reproducing the harness on a fresh machine**, detecting drift, and retiring the private `harness-backup` repository only after verified functional parity. Where something below is rejected for failing "the destination", it is one of those requirements it fails.

**Two kinds of claim appear here.** *Measurements* are properties of the installed artefacts, independently verifiable, true regardless of what is decided. *Recommendations* are conclusions drawn from them, and await review. Method is in the appendix.

## What needs deciding

1. **The per-asset recommendations** below — all of them, individually or wholesale.
2. **`caveman`'s bucket.** Two of the four survey passes disagreed and the author's answer arrived in a message truncated mid-word. Both sides are set out with the row.
3. **Is the `superpowers` fork public or private?**
4. **The fork's marketplace name.**
5. **Does `writing-specs` vendor from upstream HEAD or freeze at the 6.2.0 pin?** See [Handoff to #60](#handoff-to-60).

## Ground rules

**The ladder, the bucket rule and the `defer` state are recorded on map #53** under *Design doctrine*, along with the duplication and fork-obligation doctrines. They are not restated here; this survey applies them.

Two points bear directly on reading the tables below. **Buckets attach to rungs 1 and 2 only** — those are the rungs where something is depended on, and the three are **required** (the plugin does not work without it), **recommended** (works without it, but a user should have it) and **unrelated** (no relationship to either product; personal harness furniture). A rung 3–5 asset has no bucket rather than an empty one. And **where a plugin is rung 1 or 2, all its components come across**, so per-skill detail for those rows is informational.

Three inputs the author settled that the doctrine does not cover:

**Fork policy is per-plugin with no default.** Each call rests on its own upstream evidence, gathered as a **one-time research cost at adoption** — no scheduled re-audit. That does not freeze the decision: a material upstream change may trigger a re-audit of the affected call, the trigger being an event rather than a calendar. A plugin going unmaintained, a licence change, or a maintainer handover are the cases that would. Surfacing such a change is #63's existing job, so the trigger needs no mechanism of its own — which is separate from the two additions #63 does need for the fork, below.

**Repository count is unconstrained** — *"we can have as many repos as we want."* The three-peer framing describes the **distribution** graph, what a user installs, not a limit on what the author may own. This was the only premise that could have overturned the fork recommendation.

**Distribution of the recommended bucket is deferred** to [#96](https://github.com/eranroseman/knowledge-harness/issues/96). A README link is the interim position; a two-package split waits until the recommended list is long enough to justify one.

## How assets can physically travel

**Measured.**

**Legality.** MIT throughout — `obra/superpowers` (© 2025 Jesse Vincent), `mattpocock/skills` (© 2026 Matt Pocock). The grant covers modified copies. The binding condition is that `software-development` and `shared-skills` each ship the notice and copyright line.

**Structure.** Anything shipping *inside* a plugin must be a vendored copy in that plugin's own root. Three independent facts force it:

- The [Agent Plugins specification](https://agent-plugins.org/specification) §4.1 requires every discovered file to resolve inside the plugin root; a `SKILL.md` that does not **must be skipped silently**.
- Codex copies the plugin tree and **drops symlinks**, so a symlinked skill arrives empty.
- `~/.codex/plugins/cache/superpowers-dev/superpowers/6.2.0/.codex-plugin/plugin.json` declares `"skills": "./skills/"` — a **single path string**, not an array. No subset can be curated from one path.

`mattpocock/skills` cooperates: `find . -type l` over the whole repo returns exactly one symlink, `./AGENTS.md -> CLAUDE.md` at root, none inside `skills/`. Every skill folder is self-contained, so copying it in satisfies §4.1 with no rework.

**The consequence worth carrying:** every vendored copy, modified or not, becomes a #63 drift surface. A dependency on a **separately distributed plugin** does not, because it keeps its own plugin root. That asymmetry is why the `superpowers` fork beats vendoring its skills, and it is the reason rung 2 outranks rung 3.

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
| `caveman` | both | 1 — plugin as-is | **unrelated** *(unconfirmed)* | depend upstream |

Four rows need their reasoning stated; `superpowers` gets its own section.

**`caveman` — unconfirmed, genuinely two-sided.** *For `unrelated`:* under the necessity test nothing in `software-development` invokes it, and a public plugin recommending an output-style mode recommends taste rather than capability. *For `recommended`:* its core mode is general compressed communication a researcher benefits from identically, and only `caveman-commit` and `caveman-review` are git-specific. Two of the four passes split on exactly this. It stays installed either way; the bucket decides only whether the README names it.

**`writing-clearly-and-concisely` — depend on softaworks, as already installed.** Two premises inherited from the original brief were wrong.

*It is not a bundle.* `softaworks/agent-toolkit`'s `marketplace.json` offers **56 separate plugins**, each wrapping one capability. `enabledPlugins` carries `writing-clearly-and-concisely@agent-toolkit` and nothing else from the 56; the installed tree is one skill directory. The granularity a fork would buy is already on offer upstream.

*And obra did not fork it — the derivation runs the other way.* The brief recorded obra as forking this skill from softaworks. `obra/the-elements-of-style` was created **2025-10-14** with `isFork: false` and no parent; `softaworks/agent-toolkit` was created **2026-01-19**, its skill first appearing 2026-01-18. obra predates softaworks by three months, so a fork from softaworks is chronologically impossible. The two `SKILL.md` files are near-identical in authored wording — same "When to Use This Skill" list closing on the same bolded *"If you're writing sentences for a human to read, use this skill."*, same three-step "Limited Context Strategy" — which is copying rather than parallel invention. So **softaworks derived from obra**, permitted by obra's `"license": "Public Domain"`. The Strunk text is public domain either way; the authored wrapper establishes direction. There is no fork here and no divergence to assess.

*Which to keep: softaworks.* Two reasons, both content. **The split makes the skill's own strategy work** — both files tell the agent to dispatch a subagent with "the relevant section" under context pressure, and only softaworks can, its Strunk text being five files of 303 B to 33 KB. obra ships one 71 KB `elements-of-style.md` and warns it *"consumes ~12,000 tokens"*, describing a capability its layout does not support. And **`signs-of-ai-writing.md` has no counterpart** — 94 KB, larger than the Strunk text, covering what *not* to do. For a vault whose prose is substantially agent-drafted, that half plausibly carries more weight than the 1918 half. Totals: 178 KB against 73 KB. softaworks' description is also better shaped for invocation — *"Use when writing prose humans will read—"* is a trigger; obra's *"Apply Strunk's timeless writing rules to ANY prose"* is an instruction.

*The counterpoint, and the re-audit trigger it implies.* softaworks last pushed 2026-03-05 against obra's 2026-08-12 — nearly six months quiet. That matters little for a 1918 text, but `signs-of-ai-writing.md` is the component that decays, since AI writing tells change. **This is the plugin most likely to fire the material-upstream-change trigger**, and the thing to watch is that file rather than the commit rate.

*Before installing both:* obra's plugin is `elements-of-style` but its skill is also named `writing-clearly-and-concisely` — no plugin collision, but identical skill names, which per #89 means two catalog entries with nothing to resolve them.

**`security-guidance` ships no skills, agents or commands** — hooks and nothing else: six registrations invoking a shared entrypoint over roughly 330 KB of interdependent Python across 9 modules, plus an Agent SDK bootstrap at SessionStart with a 180-second timeout. Its Stop-hook half has no Codex equivalent; Codex's event set is `pre_tool_use`, `post_tool_use`, `permission_request`, `pre_compact`, `post_compact`, `session_start`, `session_end`, `user_prompt_submit`, `subagent_start`, `subagent_stop` — no main-agent Stop. Rung 1 avoids vendoring that Python for a Claude-only capability `codex-security` already covers by another mechanism.

**`superpowers-developing-for-claude-code` has no bucket and no fork call, because the plugin is not adopted.** Both its skills are rung-4 adaptations into `software-development` (see [The obra pair](#the-obra-pair)), so there is no dependency for a bucket to describe and nothing to fork. An earlier draft marked it `required` on the reasoning that the destination is a maintainer product; the bucket test asks whether `software-development` runs without it, and it does. Upstream is **dormant** — `pushedAt` 2025-12-03, main HEAD equal to the `v0.3.1` tag equal to the installed pin `74afe935`, nine months with no unreleased work — which makes vendoring the easy case rather than the risky one.

## superpowers — fork it

**Nature.** The author's position on as-is adoption is an observation, not a ruling — verbatim: *"I didn't rule that superpowers can't be adopted as-is. I said unfortunately the evidence suggests it is impossible."*

**Rung 1 fails — measured.** `hooks/hooks.json` registers a SessionStart hook on matcher `startup|clear|compact`, and `hooks/session-start` injects `skills/using-superpowers/SKILL.md` verbatim inside `<EXTREMELY_IMPORTANT>` tags. That file routes to the skill being replaced, by qualified name, twice — line 22, *"**Before entering plan mode:** if you haven't already brainstormed, invoke the brainstorming skill first"*, and line 30, *"`\"Let's build X\"` → superpowers:brainstorming first, then implementation skills"*.

So rung 1's cost is not a passive catalog duplicate a better description could out-compete. It is an always-on injected directive naming the competitor — and once inside, `brainstorming`'s `<HARD-GATE>` and its *"The ONLY skill you invoke after brainstorming is writing-plans"* clause foreclose handing back. The failure is not "picks arbitrarily"; it is "reliably picks the replaced skill, then locks the door."

**And it cannot be muted — measured against the installed binary** at `~/.local/share/claude/versions/2.1.220`:

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

`e.source === "plugin"` returns `"on"` unconditionally; the override map is never reached. The branch above it is not a plugin path — `sPy` is `new Set(["auto-mode-setup"])`, one built-in command. Corroborated twice in the same binary: the `/skills` UI excludes entries where `loadedFrom !== "skills" && loadedFrom !== "commands_DEPRECATED"`, and `/plugin` exposes only `plugin:toggle` and `plugin:install`. Codex is more total, not less: `codex plugin --help` on codex-cli 0.147.0 lists only `add`, `list`, `marketplace`, `remove`; there is no `codex skill` subcommand and `~/.codex/config.toml` carries no skill-level key.

This settles #60's open question, though that question was framed on a borrowed authority. #60 asked whether *"`skillOverrides` cannot patch plugin skills"* had gone stale, citing research-vault's foundation specification §7 — which governs **that** product. `software-development` inherits no doctrine from it. What settles the question is the fact itself, verified above.

**Rung 3 — vendoring its components — fails too, measured.** The wanted skills carry **26** hard-coded `superpowers:`-qualified cross-references across 9 files, on 25 lines (one line carries two), verified by `grep -ro` against the installed cache. **None sits inside `skills/brainstorming/`**, so every one survives that directory's deletion and every one breaks under vendoring.

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

The breakage class is permanent: 20 commits since 2026-01-01 touched `superpowers:` strings under `skills/`, `writing-skills/SKILL.md:283` prescribes the qualified form as house style, and such changes **auto-merge without conflict** — so each future one lands silently broken. Copying these skills out therefore requires editing 26 references, which is rung 4 by definition. That is specific to `superpowers`: vendoring by itself does not push rung 3 to rung 4, since a byte-identical copy stays at rung 3.

**Rung 2 — fork — is the answer.** Qualified names are `pluginName:skillName`, independent of marketplace, corroborated live against `superpowers-developing-for-claude-code:developing-claude-code-plugins`, namespaced by plugin name while its marketplace is `superpowers-developing-for-claude-code-dev`. **Keeping `"name": "superpowers"` preserves all 26 references untouched.**

Measured by building the fork at pin `44c9b2d6` and merging upstream HEAD `b36e0829` (v6.3.0, five weeks, 415 lines across 13 skill files):

- Patch: **10 files changed, 117 insertions, 1933 deletions** — delete `skills/brainstorming/`, edit two lines of `using-superpowers/SKILL.md`, replace the `AGENTS.md` symlink with a regular file.
- Merge: **exactly two conflicts**, both `DU` on the deleted directory, resolved by `git rm -r`, fully scriptable.
- The one file the fork edits **auto-merged cleanly** even though upstream touched it.

**Upstream health, for the fork call.** `obra` (Jesse Vincent), 279,648 stars, last push 2026-08-29, monthly releases (v6.1.0 06-30, v6.2.0 07-24, v6.3.0 08-12), 100 commits touching `skills/` since 2026-06-01. No `eranroseman` fork exists. **The machine is pinned at 6.2.0 while v6.3.0 shipped 2026-08-12** — one minor behind, and that delta touches 13 skill files across 7 skills.

**Asking upstream instead is a non-starter.** `brainstorming` is the plugin's first manifest keyword and its `defaultPrompt` is *"I've got an idea for something I'd like to build."* — the front door obra is selling, not an incidental skill.

**A fourth arrangement, rejected.** Claude Code marketplace entries can declare a plugin's components — the binary carries *"has conflicting manifests: both plugin.json and marketplace entry specify components. Set `strict: true` in marketplace entry or remove component specs from one location."* Since upstream's `.claude-plugin/plugin.json` declares no components, an entry-level `skills` array selecting 13 of 14 would conflict with nothing: curation with no fork and no vendoring. **It dies on Codex**, whose single-path `skills` key cannot express a subset, so it fails the cross-harness requirement.

**Three live defects a fork lets you fix — each by a different act.**

| Defect | Fixed by |
|---|---|
| Codex's `[marketplaces.superpowers-dev]` is `source_type = "local"`, pointing into `~/.claude/plugins/marketplaces/`, so the Codex install is parasitic on a Claude install having happened first and **cannot reproduce on a fresh machine**. Every other Codex marketplace here is `source_type = "git"`. | Publishing the fork at a **git URL** |
| #56's missing Codex `AGENTS.md`: `git ls-files -s AGENTS.md` returns mode `120000` (a tracked symlink) while `git status --porcelain` reports ` D AGENTS.md` and no file exists on disk. Codex drops the symlink, so 8,873 bytes of plugin-level guidance are silently absent. | The **10-file patch**, which commits it as a regular file |
| Codex's manifest declares `"hooks": {}`, so **superpowers' SessionStart hook does not fire on Codex at all**, though `hooks/` is copied there. Codex supports `session_start` and sets `CLAUDE_PLUGIN_ROOT`; superpowers simply does not wire it. | **Nothing yet.** The measured patch does not wire it either — a fork makes the fix *possible*; someone still has to author it. Route to #61 |

**Known gaps.** The fork patch is under-scoped as measured: `tests/brainstorm-server/` holds 12 live test files hard-coding `skills/brainstorming/scripts/...`, all orphaned by the deletion. And a fork nobody merges becomes a stale private snapshot — the failure `harness-backup` exists to avoid, reintroduced elsewhere. **Without #63's merge-base monitor the fork is strictly worse than rung 1**, so that monitor is a precondition rather than an enhancement.

**This reverses a clause of [#72](https://github.com/eranroseman/knowledge-harness/issues/72)**, which recorded the process spine as "adopted as-is" while simultaneously vendoring `brainstorming` out of it — two statements that cannot both hold at plugin granularity. Recorded as a dated reversal per the precedent [#77](https://github.com/eranroseman/knowledge-harness/issues/77) set over [#89](https://github.com/eranroseman/knowledge-harness/issues/89). Everything else in #72 stands; **only the adoption mechanism changes.** The reversal is this ticket's to make, drawn from the measurements above — not an author ruling.

## mattpocock's skills — 18 installed

Installed standalone via `~/.agents/.skill-lock.json`, not as a plugin. All adopted skills are **rung 3, vendored** into whichever product needs them.

- **To `shared-skills`:** `grilling`, `research`, `handoff`, `teach`, `to-questionnaire`, `wait-what`, `wayfinder`, `wizard`, `writing-for-agents`.
- **To `software-development`:** `codebase-design`, `prototype`, `resolving-merge-conflicts`, `improve-codebase-architecture`, `triage`, `domain-modeling`.
- **Rung 4, adapt:** `setup-matt-pocock-skills`.
- **Not adopted:** `grill-with-docs`, `to-tickets`, per #72's process-skill ruling.

Six were independently hash-matched against exact upstream commits and are **pristine but stale** — `domain-modeling` @ `54bc6b6`, `triage` @ `6a34259e`, `writing-for-agents` @ `4aaccb58`, `setup-matt-pocock-skills` @ `c66bdee`, `grilling` @ `86cba45f`, `wayfinder` @ `6a34259e`.

**`domain-modeling` is `software-development` only — and the reasoning that nearly put it in `shared-skills` was wrong.** An earlier pass argued the call graph forced it: `wayfinder` is shared and invokes `domain-modeling` at three unconditional sites — the default ticket type (*"Always call the Skill tool twice"*, line 79), the mandatory first act of charting a map (*"Name the destination. Call the Skill tool twice"*, line 111), and the fallback at line 124 — so a research-vault-only install would leave the call dangling.

That test optimised for closing the call graph rather than for the right thing happening, and it never weighed what presence costs against what absence costs.

*Presence is not neutral.* The skill is thoroughly repo-shaped: its description reads *"Use when discussing **codebase** terminology, writing or editing a **CONTEXT.md**, or recording or editing an **ADR**"*; its structure section opens *"Most **repos** have a single context"* and diagrams `src/`, `docs/adr/`, `CONTEXT.md`; it carries a *"Cross-reference with code"* step and ships `ADR-FORMAT.md` and `CONTEXT-FORMAT.md`. A scaffolded vault has none of those artefacts — `templates/`, what `setup-vault` ships, contains neither `CONTEXT.md` nor `docs/adr/`. And the skill creates what it does not find: *"If no `CONTEXT.md` exists, create one when the first term is resolved. If no `docs/adr/` exists, create it when the first ADR is needed."* So a shared `wayfinder` invoking it in a vault session would write code-project scaffolding into an OKF-conformant vault — damage to the artefact `research-vault` exists to protect, not clutter.

*Absence costs a retry.* The Skill tool errors, the agent proceeds, and no domain modelling happens — which is correct where the discipline does not apply.

Two ways to remove the dangling call if it proves irritating in practice, neither taken now: adapt `wayfinder` so its grilling ticket type does not invoke `domain-modeling` unconditionally, which moves it from rung 3 to rung 4 and buys a permanent adaptation; or leave it, since the error is visible to the agent and costs one retry.

**`prototype` is the same shape and the same answer.** `wayfinder` calls it at one site, reached only when a prototype ticket is created. Its absence degrades `wayfinder` to three ticket types, and a researcher plausibly never reaches for *"a throwaway prototype... UI/logic code"*.

**Why not fork `mattpocock/skills`, given rung 2 outranks rung 3?** Four reasons, the first decisive.

- **Forking buys nothing here.** The whole justification for the `superpowers` fork is namespace preservation, and it does not apply: `grep -ro 'mattpocock-skills:'` across the installed set returns **zero**. Every cross-reference is a bare name — `grilling` referenced by `improve-codebase-architecture`, `triage` and `wayfinder`; `domain-modeling` by three; `prototype` by two — and bare names survive relocation.
- **Two forks would collide on the name.** The adopted skills split across two distributables, so one fork cannot serve both, and two forks cannot both be `mattpocock-skills`. At least one must be renamed, paying a rename cost for a namespace benefit that does not exist.
- **Doubled merge burden on a live upstream**, each fork maintaining a different deletion set indefinitely.
- **Recategorisation would become a two-repository transaction** — a delete in one fork and an add in the other, in lockstep, where vendoring makes it a file move.

A fifth consideration is structural: `shared-skills` holds **plugin components and nothing else** (author, 2026-08-30, clarifying #77 — whose "nothing else" targeted `terminology.md` and glossaries, not components). A fork of someone else's repository minus 28 skills is not a component set.

## mattpocock's skills — 19 not installed

**Scope caveat.** #75's declared inventory sources are what is *installed*. These nineteen were surveyed at the author's request for completeness, so they sit outside the ticket's own scope and their verdicts carry correspondingly less authority — a reading of upstream, not a disposition of an installed asset.

The upstream roster is 37 skills — engineering 18, productivity 7, in-progress 8, misc 4 — certified by mechanical set-diff against `find skills -name SKILL.md`, empty in both directions.

**Fifteen are recommended not adopted:** `ask-matt`, `code-review`, `implement`, `tdd`, `to-spec`, `grill-me`, `claude-handoff`, `implement-spec`, `loop-me`, `retro`, `setup-ts-deep-modules`, `git-guardrails-claude-code`, `migrate-to-shoehorn`, `scaffold-exercises`, `setup-pre-commit`. Adoption of something the author currently lives without required naming a concrete gap it fills; none did.

**Four were parked, not declined, and the survey could not say so.** The standing recommendations register (`docs/product-landscape/2026-08-25-coding-companion-plugins-comparison.md`) parks each with an explicit trigger; it was not supplied to the assessment passes, which is why they missed this. Before the `defer` state existed, a parked skill was indistinguishable from a rejected one and all four printed as `not-adopted`.

| Skill | Register's trigger | Correct state |
|---|---|---|
| `diagnosing-bugs` | *"evaluate at the next real debugging need"* (register item 09) | **adopt now, rung 4** |
| `writing-fragments` | *"serious candidates for workload 3's map"* | defer to workload 3 |
| `writing-beats` | same | defer to workload 3 |
| `writing-shape` | same | defer to workload 3 |

If the writing suite is adopted at workload 3 it lands at **rung 3 with a vendored snapshot**, because upstream marks all three in-progress — *"can change or disappear"*.

**`diagnosing-bugs` is a correction rather than a deferral: adopt at rung 4, hard-gated to explicit invocation.** Both decline reasons were true only of as-is adoption. *The Codex miscalibration is real* — upstream documents it over-firing on non-Claude models, four reports on issue #578 — *and the fix is the vendor's own prescription*: `policy:\n  allow_implicit_invocation: false` in `agents/openai.yaml`, already shipped upstream on `ask-matt` and `implement`. Two lines. *The trigger race with `superpowers:systematic-debugging`* is resolved by the same gating plus a Claude-side `user-invocable-only` override while the skill remains lockfile-installed.

The register backs it with the strongest evidence in this survey — not an opinion about a skill but **an audited failure of this repository's own work**, validation item 5: *"the run's most expensive error class (instrument scope — the `.pop()` measurement missing `{\"date-parts\": []}`) maps onto its Phase-1 red-capable-loop criterion; systematic-debugging has no equivalent."*

That gap is confirmed by reading both skills, and it is worse than a missing feature. **On the one point where the two overlap the spine is inverted**: `systematic-debugging`'s Iron Law gates *fixes* on investigation; `diagnosing-bugs` gates *investigation* on a red-capable command existing. The spine carries no loop-construction material anywhere — not in `SKILL.md`, `root-cause-tracing.md`, `defense-in-depth.md` or `condition-based-waiting.md`.

A complementary option, cheap and licence-clean: the fork puts `skills/systematic-debugging/` under the author's control, so `building-a-feedback-loop.md` could sit beside `root-cause-tracing.md` carrying the Phase-1 ladder and the red-capable criterion, with provenance. That transfers the *method* but not the *gate*, so it complements hard-gated adoption rather than replacing it.

**One register recommendation is stale, resolved in this survey's favour.** The register proposes *"de-fanging the injection selectively in settings (`skillOverrides` name-only, the grilling precedent) gets nearly all the benefit at none of the fork cost."* It does not work, and the diagnosis is precise: **`grilling` is lockfile-installed, where `skillOverrides` does reach.** The register generalised that precedent to plugin skills, where the resolver returns `"on"` before consulting the override map.

## The obra pair

`working-with-claude-code` and `developing-claude-code-plugins` are each installed **twice** — inside the `superpowers-developing-for-claude-code` plugin, and standalone via the lockfile from the same upstream. Both live simultaneously.

**Both are rung 4, both to `software-development`, neither shared.** They separate on *consumer* rather than depth: `developing-claude-code-plugins` is an authoring workflow whose artefacts are `.claude-plugin/plugin.json`, `marketplace.json`, `hooks.json` and git tags; `working-with-claude-code` is a runtime reference whose nine "When to Use" triggers are all harness extension, configuration and troubleshooting. A researcher produces neither class of artefact.

**What forces rung 4, and decides the dedupe: each install is broken in a way the other masks.**

- The **plugin's** `working-with-claude-code` hardcodes standalone paths — `SKILL.md:119` reads `path: ~/.claude/skills/working-with-claude-code/references/`, `SKILL.md:132` invokes `node ~/.claude/skills/working-with-claude-code/scripts/update_docs.js`, and `${CLAUDE_PLUGIN_ROOT}` appears **zero** times. Neither resolves from a plugin install; they resolve today only because the standalone copy exists.
- The **standalone** `developing-claude-code-plugins` references `examples/simple-greeter-plugin/` and `examples/full-featured-plugin/` in three places, but those live at **plugin root**. The lockfile install ships no examples at all.

**So the dedupe is: keep both now, drop both later.** An earlier draft recommended keeping the plugin and dropping the lockfile entries; that is wrong on this evidence, since removing either copy today breaks the other. `software-development` ships the adapted copies first, at which point both current installs become redundant together. **The adaptation is what makes deduplication safe, not a precondition of it.** Routes to #60 and #62 as one motion.

**A drift asymmetry for #63.** `working-with-claude-code`'s true upstream is not obra: its 42 reference files are generated from `docs.claude.com` by the bundled `scripts/update_docs.js`, and they are stale — missing `skillOverrides`, plugin `dependencies`, and `allowCrossMarketplaceDependenciesOn`, all three of which this programme now relies on. Its drift question is "have Anthropic's docs moved", not "has obra committed", so a monitor watching the obra pin reports clean while the content rots.

## The four harness-backup skills

Recommendation only — the owning tickets decide.

| Skill | Rung | Home | Owning ticket |
|---|---|---|---|
| `consistency-audit` | 3 — vendor | **`shared-skills`** | #79 |
| `rethink-audit` | 3 — vendor | `software-development` | #73 |
| `rethink` | **not adopted — drop** | — | #73 |
| `finding-duplicate-functions` | 4 — adapt | `software-development` | #60 |

**`consistency-audit` is shared, correcting an earlier verdict.** Its description is *"contradictions, duplication, drifted terms, stale claims"* — what a research vault accumulates at least as much as a code repository does. The earlier `software-development`-only call was reached from framing vocabulary (*"read a **repository** whole"*) rather than capability. The skill degrades gracefully by design: *"Most repositories have none of these. When one is absent, proceed with the defaults and say nothing."*

Its subagent travels with it. `consistency-audit` hard-dispatches `consistency-audit-inspector` at `SKILL.md:78` (*"two independent readers over every slice"*) and `:116` (*"instructed to refute"*), and that agent lives outside the skill directory at `~/harness-backup/claude/agents/`. Under a reading of #77 as *skills* and nothing else this would have blocked the assignment; under the clarification that `shared-skills` holds **plugin components**, an agent qualifies. #51 flagged this agent as sitting outside the drift detector's watched set and deferred it to #78 — still open, and now more load-bearing since the agent becomes shipped rather than local.

**`rethink` is dropped, on duplication rather than principle.** Its entire body is one sentence: *"Run a `/rethink-audit` pass on a fresh design question: no implementation exists, so work through `design:` and finish at `trade-offs:`."* `rethink-audit` already carries that at line 60: *"On a fresh design question there is no implementation: run through `design:`, then `trade-offs:`."* Near-verbatim — not a wrapper adding a parameterisation but a restatement of a line inside the skill it delegates to.

This answers #73's second question differently from how that ticket frames it: the front door does not absorb `/rethink` and it does not survive as a distinct entry point — **`rethink-audit` absorbed it already.** It also means `rethink-audit` needs no adaptation for the fresh-design case, keeping it at rung 3.

**`rethink-audit` is `software-development`, but weakly.** Its method reconstructs `requires:` "from its boundary — signatures, call sites, tests" and reads "the current implementation" at `gap:`, with migration cost as the frame — that needs code. The usage evidence argues wider: of seven audits in `docs/research/rethink-audits/`, several are not code (`controller-protocol`, `development-process`, `glossary-and-adr-triage`, `coding-companion-plugin-layering`). All remain engineering-domain, so the verdict holds as a borderline call. Both skills ship `agents/openai.yaml`, so they are cross-harness ready.

The author has separately ruled that `rethink`/`rethink-audit` land in either `software-development` or `shared-skills`, and that **both** the public `eranroseman/rethink` repository and the harness-backup copies are deleted. Recorded on #73.

## The six sharing verdicts this ticket owed

Four were deferred here by #89 — `domain-modeling`, `triage`, `writing-for-agents`, `setup-matt-pocock-skills`. Two more were left unforced — `working-with-claude-code` and `superpowers`. All six rest on the skill bodies rather than on folder names.

| Skill | Verdict |
|---|---|
| `writing-for-agents` | `shared-skills` |
| `domain-modeling` | **`software-development`** — repo-shaped (CONTEXT.md, ADRs, cross-reference with code) and it *creates* those artefacts where absent, so shipping it to a vault is damage rather than clutter. `wayfinder`'s unconditional call to it dangles on a vault-only install, which is the correct outcome |
| `triage` | `software-development` |
| `working-with-claude-code` | `software-development` |
| `superpowers` | `software-development` — meaning **`software-development` depends on it and `research-vault` does not**. The fork stays a separate plugin with its own root; this axis assigns which product needs the capability, not where files sit |
| `setup-matt-pocock-skills` | **the axis does not apply** — it is a rung-4 template feeding #62's setup mechanism, not a capability either product ships |

`working-with-claude-code` is the one reversal. It was argued during the grilling as shared, on the grounds that it documents the runtime both products run on; two passes placed it with engineering for the reasons given under [The obra pair](#the-obra-pair).

## Handoff to #60

Every asset landing on rung 4, copy-consumable.

| Asset | What must change |
|---|---|
| `brainstorming` → `writing-specs` | Rename; correct the description, which promises open-ended ideation while the body is a one-way funnel from idea to committed spec with a mandatory approval gate; decide the Visual Companion; decide the base version |
| `setup-matt-pocock-skills` | Adapt as the template for #62's setup mechanism, per #85 |
| `working-with-claude-code` | Rewrite the two hardcoded paths to `${CLAUDE_PLUGIN_ROOT}`-relative form; re-run `update_docs.js` to refresh the 42 references |
| `developing-claude-code-plugins` | Co-locate or re-path the two `examples/` directories; subordinate Phase 1 (Plan) and Phase 6 (Release) to `superpowers:writing-plans` and `superpowers:finishing-a-development-branch` so #72's spine is not duplicated |
| `finding-duplicate-functions` | Provenance header against `obra/superpowers-lab`; the local copy is a substantial rewrite, shell replaced with Python |
| `diagnosing-bugs` | Add `policy:\n  allow_implicit_invocation: false` to `agents/openai.yaml`; gate Claude-side invocation |

All six need a provenance header; the table lists what is needed beyond that.

**The list shrank because of the fork.** Earlier passes marked `systematic-debugging`, `test-driven-development`, `writing-plans`, `writing-skills` and `using-superpowers` as rung-4 adaptations. Those were artefacts of the vendoring branch — a fork keeps the namespace, so none needs adaptation as a *vendored copy*. `using-superpowers` is still edited, but inside the fork as two lines of its ten-file patch, which is the fork's business rather than #60's. That collapse is the fork's clearest practical benefit.

**Two decisions #60 must make knowingly.**

*The Visual Companion is separable but not free.* It is 1,730 lines — `scripts/server.cjs` 723, `scripts/frame-template.html` 213, `scripts/start-server.sh` 209, `scripts/helper.js` 167, `scripts/stop-server.sh` 120, plus `visual-companion.md` 298 — within a `brainstorming` directory totalling 1,930 lines across 8 files. Nothing outside that directory references it, so dropping it costs one file deletion, one directory deletion and about 19 lines from the body. But removing those 19 lines means *"internals untouched"*, which is what #72 specified, no longer describes the vendoring. The companion also loads a logo from an external site carrying the Superpowers version, opt-out via `SUPERPOWERS_DISABLE_TELEMETRY`.

*The base version matters.* Upstream HEAD replaced `brainstorming` with a three-path Spike/Bounded/Architectural router — 117 changed lines — **after** the 6.2.0 text #72 judged. Vendoring from the pin ships a skill already a generation behind. Vendor from HEAD, freeze deliberately, or place `writing-specs` under #63's drift watch as a tracked adaptation.

## Handoff to other tickets

**#62 — hard sequencing, and a migration.** The fork's edited bootstrap points at `software-development:writing-specs`. Until that ships, every session injects a route, inside `<EXTREMELY_IMPORTANT>` tags, to a skill that does not exist, so `writing-specs` must land before or with the cutover. The cutover must also uninstall first on both harnesses, because the fork keeps the plugin name and collides with the installed copy. **Two installs must be migrated, not one:** `installed_plugins.json` carries a project-scope entry for `/home/eranr/memoria-vault` at `gitCommitSha` `3dcbd5c4…` while the user-scope entry has `44c9b2d6…`, both naming the **same** `installPath`. Easy to miss, and it establishes that install path does not imply pin — which #63 and #78 should know independently.

**#63 — two additions.** Watch upstream HEAD against the fork's merge-base, not just the fork against the installed cache — a precondition, as the fork section states. And catch **unqualified** references: upstream already added `skill_view("brainstorming")` to `using-superpowers/references/hermes-tools.md:31`, which auto-merges clean and is invisible to a `grep superpowers:brainstorming`.

**#61 — a live constraint, not a blank slate.** A SessionStart injection already fires every startup/clear/compact from the forked superpowers, carrying the skill-invocation discipline. #61 must decide whether `software-development`'s own hook composes with that or duplicates it; Claude Code merges hooks from multiple plugins without dedup. The two edited routing lines in `using-superpowers/SKILL.md` are a supported seam and merge cleanly.

**#64 — two.** The declared-asset policy gap (below), and **`finding-duplicate-functions` is absent from `harness-backup`'s README entirely**, so a fresh-machine restore silently omits it.

**#81 — `to-spec` is mattpocock's PRD skill, renamed.** `CHANGELOG.md:181` — *"`to-prd` is renamed to `to-spec`"*; `docs/engineering/to-spec.md:38` — *"Where did `/to-prd` go? It is this skill, renamed in v1.1."* So #81's premise that no vendor's roster contains one is wrong in letter. It is worth more as a cited failure mode than as a donor, because upstream documents its own defect at `docs/engineering/to-spec.md:57`: *"The template leans hard on user stories, which is the wrong shape for architectural work: you end up writing stories nobody asked for around decisions that are really about interfaces and invariants."* Its template divides along exactly the line #81 must draw — product: Problem Statement, Solution, User Stories; engineering: Implementation Decisions, Testing Decisions; shared: Out of Scope, Further Notes. Also minable: `triage/AGENT-BRIEF.md`, 207 lines, MIT, already installed.

**#59 and #69 — a working cross-harness exemplar.** `obra/the-elements-of-style` carries generated manifests for eight harnesses in one source repository — `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.devin-plugin/`, `.hermes-plugin/`, `.kimi-plugin/`, `.opencode/`, `.pi/`, plus `.agents/plugins/marketplace.json` — produced and checksummed by a tool, recorded in `.everyharness/manifest.json` as `"tool": "everyharness@0.7.0"`. That is a live answer to the question #59 asks about serving two harnesses from one source, and it bears on #69's conformance check. Worth reading before either invents a layout.

**#78 — an offered requirement.** See anomaly 1 below.

## The five anomalies #75 carried

1. **The orphaned-cache count in the ticket body is wrong.** Of 16 directories under `~/.claude/plugins/cache/`, nine are enabled pins. Of the remaining seven: three are superseded versions of still-enabled plugins (garbage-collection lag from a batch update on 2026-08-10); three are **true orphans** with no enabled successor — `interface-design`, `pr-review-toolkit`, `frontend-design`, where the ticket named only the first; and one, `caveman/caveman/17f9f2ec2377`, is unreferenced **and unmarked**, with a larger roster than the pin. Filed as [#95](https://github.com/eranroseman/knowledge-harness/issues/95) and ruled out of scope for map #53 as machine hygiene.

   *The finding for #78:* the client's own `.orphaned_at` marker is **not** a complete signal — six of seven carry it and one does not — so a doctor check that trusts it misses exactly the case most warranting a human look. Set subtraction against `installPath` is the reliable test. Offered as an inherited requirement, to take or decline.

2. **The double-installed obra skills** — decided under [The obra pair](#the-obra-pair).

3. **The dormant `rethink` marketplace** routes to #73 as one motion with the placement and deletion calls, per #51's deliberate bundling — deleting the upstream repository makes the registration dead by definition.

4. **The empty `claude-plugins-official` marketplace** is out of scope, filed with #95. It is a different registration from `claude-code-plugins`, which supplies the live `security-guidance` and must not be removed alongside it.

5. **The declared-asset policy gap was mislocated in the ticket body.** It is not in this repository's `AGENTS.md`; it lives in the global `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`, both covering only the `npx skills add -g` path with no declared-asset surface for native installs. Routed to #64 by the author, on the reasoning that a hand-maintained table is the weakest tier under this repo's *eliminate > mechanism > rule > prose* ordering and goes stale on the next install.

## Appendix: method

Four adversarially-verified survey passes, plus a fifth cross-checking them against the standing recommendations register. Each assessed on evidence read off disk or fetched from upstream, then was refuted by an independent agent instructed to default to rejection where a claim rested on a description rather than a file body. Where the text above cites "two of the four passes", that is the denominator.

Sources read fresh rather than inherited from earlier tickets: `~/.claude/settings.json`, `~/.claude/plugins/installed_plugins.json`, `~/.claude/plugins/known_marketplaces.json`, `~/.claude/plugins/cache/`, `~/.codex/config.toml`, `~/.codex/plugins/cache/`, `~/.agents/.skill-lock.json`, `~/harness-backup/claude/skills/`, and the installed Claude Code binary at `~/.local/share/claude/versions/2.1.220`.

Where a claim decided a branch it was re-verified by hand outside the surveys — the override resolver, the cross-reference count, the upstream licence and repository statistics, the Codex manifest, and the `writing-clearly-and-concisely` derivation chronology. Four figures the surveys reported were corrected that way: the cross-reference count (24 and 25 were both reported; 26 is correct), the upstream licence (`gh repo view` reported none; the licence endpoint confirms MIT), the orphaned-cache count, and the obra/softaworks derivation, inherited from the ticket brief as a fork by obra from softaworks and found to be neither a fork nor in that direction.

**One methodological failure worth recording**, because it produced four wrong verdicts rather than one: the standing recommendations register was never supplied to the four assessment passes, so the nineteen not-installed skills were judged without the repository's own prior evidence about them. The fifth pass exists only because that was noticed afterwards.
