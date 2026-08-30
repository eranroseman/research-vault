# Installed asset disposition survey

**Status: recommendation. Nothing here is approved.**
**Date:** 2026-08-30 · **Ticket:** [#75](https://github.com/eranroseman/knowledge-harness/issues/75), a `wayfinder:grilling` ticket on map [#53](https://github.com/eranroseman/knowledge-harness/issues/53)

Every plugin and skill installed on this machine across Claude Code and Codex, plus the full upstream `mattpocock/skills` roster including the 19 skills not installed here, and the four `harness-backup`-owned skills. Each gets a ladder step, a bucket, a sharing verdict, and — for plugins — a fork call.

Companion to the [2026-08-28 alteration-inventory sweep](2026-08-28-alteration-inventory-sweep.md), which asked whether assets had drifted. This one asks what to do with them.

**The destination**, as map #53 states it and as several judgements below appeal to: an installable cross-harness plugin that is the canonical home for shared authored and deliberately adapted guidance and automation, running on **both Claude Code and Codex**, **reproducing the harness on a fresh machine**, detecting drift, and retiring the private `harness-backup` repository only after verified functional parity. Where something below is rejected for failing "the destination", it is one of those requirements it fails.

Two kinds of claim appear here and they have different standing:

- **Measurements** are properties of the installed artefacts, independently verifiable, and true regardless of what is decided.
- **Recommendations** are conclusions drawn from those measurements. They await review.

Method is in the appendix.

## What needs deciding

1. **The per-asset recommendations** in [Recommendations](#recommendations) — all of them, individually or wholesale.
2. **`caveman`'s bucket** — two of the four survey passes disagreed, and the author's answer arrived in a message truncated mid-word. Both sides are set out with the row.
3. **The obra double-install dedupe** — recommended but resting on the same truncated message.
4. **Is the `superpowers` fork public or private?**
5. **The fork's marketplace name.**
6. **Does `writing-specs` vendor from upstream HEAD or freeze at the 6.2.0 pin?** See [Handoff to #60](#handoff-to-60).

## Settled inputs

These were answered directly by the author and are not in question.

**The ladder**, which replaced this ticket's original adopt-as-is / modify-import / unrelated axis:

1. **Plugin as-is.** Depend on it unchanged. A plugin is all its components — skills, hooks, subagents, slash commands, MCP servers.
2. **Fork plugin.** Take the whole repository, patch it, publish it, depend on your copy.
3. **Vendor component.** Copy selected components into your own plugin root, unmodified.
4. **Adapt component.** The same copy, modified, carrying provenance.
5. **Write one.**

**The rungs are ordered by what you take on against what upstream still gives you**, which is what makes this a test rather than a taxonomy:

| Rung | You own | Upstream reaches you by |
|---|---|---|
| 1 plugin as-is | nothing | automatically |
| 2 fork plugin | a patch | `git merge` |
| 3 vendor component | the copy | re-vendoring |
| 4 adapt component | the copy and a delta | re-vendoring, then re-applying your edits |
| 5 write | everything | not at all |

Two consequences of the shape. **Granularity changes at rung 3**: rungs 1 and 2 are whole-artefact, rungs 3–5 are per-component, which is why only the latter say *component*. And **buckets attach to rungs 1 and 2 only** — those are the rungs where you depend on something, so required / recommended / unrelated has something to describe. Rungs 3–5 are contained content and take no bucket.

Rungs 3–5 read *component*, not *skill*, deliberately. The difference between rung 3 and rung 4 is **provenance**, so confining them to skills would force any adapted hook, subagent or command up to rung 5 — silently stripping the provenance obligation and leaving #63 nothing to watch. #61's lean-router SessionStart hook is a live case.

**The buckets**, which apply to rungs 1 and 2. Anything depended on is exactly one of **required** (the plugin does not work without it), **recommended** (works without it, but a user should have it), or **unrelated** (no relationship to either product; personal harness furniture).

**Fork policy is per-plugin with no default.** Every fork-or-depend call rests on its own upstream evidence, and gathering it is a **one-time research cost at adoption** rather than a recurring one — there is no scheduled re-audit.

That does not freeze the decision. **A material upstream change may trigger a re-audit of the affected call** — the trigger is an event, not a calendar, and it re-opens the question rather than answering it. A plugin going unmaintained, a licence change, or a maintainer handover are the cases that would. #63 is already where such a change surfaces, since it watches upstream, so this needs no separate mechanism.

**Repository count is unconstrained** — *"we can have as many repos as we want."* The three-peer framing (`research-vault`, `software-development`, `shared-skills`) describes the **distribution** graph, what a user installs, not a limit on what the author may own. This was the only premise that could have overturned the fork recommendation, so the fork below stands on its own merits rather than on any scarcity of repositories.

**Distribution of the recommended bucket is deferred** to [#96](https://github.com/eranroseman/knowledge-harness/issues/96). A README link is the interim position; a two-package split — dependencies-only plus a bundle — waits until the recommended list exists and is long enough to justify one.

**The first function of `software-development`** is to be the single home for the non-as-is assets, so they are managed in one designated location rather than per repository.

## How assets can physically travel

**Measured.**

**Legality.** MIT throughout — `obra/superpowers` (Copyright (c) 2025 Jesse Vincent), `mattpocock/skills` (Copyright (c) 2026 Matt Pocock). The grant covers modified copies. The binding condition is that `software-development` and `shared-skills` each ship the notice and copyright line.

**Structure.** Anything shipping *inside* a plugin must be a vendored copy in that plugin's own root. Three independent facts force it:

- The [Agent Plugins specification](https://agent-plugins.org/specification) §4.1 requires every discovered file to resolve inside the plugin root; a `SKILL.md` that does not **must be skipped silently**.
- Codex copies the plugin tree and **drops symlinks**, so a symlinked skill arrives empty.
- `~/.codex/plugins/cache/superpowers-dev/superpowers/6.2.0/.codex-plugin/plugin.json` declares `"skills": "./skills/"` — a **single path string**, not an array. No subset can be curated from one path.

`mattpocock/skills` cooperates with this: `find . -type l` over the whole repo returns exactly one symlink, `./AGENTS.md -> CLAUDE.md` at root, none inside `skills/`. Every skill folder is self-contained, so copying it in satisfies §4.1 with no rework.

**The consequence worth carrying:** every vendored copy, modified or not, becomes a #63 drift surface. A dependency on a **separately distributed plugin** does not, because it keeps its own plugin root.

## Recommendations

Plugin-level disposition is the operative call. **Where a plugin is rung 1 or 2, all its components come across and per-skill detail is informational only.**

| Plugin | Harness | Step | Bucket | Fork call |
|---|---|---|---|---|
| `superpowers` | both | **2 — fork plugin** | required | **fork** |
| `superpowers-developing-for-claude-code` | Claude | 4 — adapt its two skills | n/a — plugin not adopted | no fork; upstream dormant |
| `obsidian` | both | 1 — plugin as-is | recommended | depend upstream |
| `writing-clearly-and-concisely` | both | 1 — plugin as-is | recommended | depend upstream (softaworks) |
| `diataxis-skills` | both | 1 — plugin as-is | recommended | depend upstream |
| `codex` (openai-codex bridge) | Claude | 1 — plugin as-is | recommended | depend upstream |
| `codex-security` | Codex | 1 — plugin as-is | recommended | depend upstream |
| `security-guidance` | Claude | 1 — plugin as-is | recommended | depend upstream |
| `ponytail` | both | 1 — plugin as-is | recommended | depend upstream |
| `caveman` | both | 1 — plugin as-is | **unrelated** *(unconfirmed)* | depend upstream |

Four rows need their reasoning stated.

**`caveman` — unconfirmed, and genuinely two-sided.** *For `unrelated`:* under the necessity test nothing in `software-development` invokes it, and a public plugin recommending an output-style mode recommends taste rather than capability. *For `recommended`:* its core mode is general compressed communication that a researcher benefits from identically, and only two of its skills — `caveman-commit` and `caveman-review` — are git-specific. Two of the four survey passes split on exactly this. It stays installed either way; the bucket only decides whether the README names it.

**`writing-clearly-and-concisely` — depend on softaworks, as already installed.** Two premises inherited from the original brief turn out to be wrong, and both are corrected here.

*It is not a bundle.* `softaworks/agent-toolkit`'s `marketplace.json` offers **56 separate plugins**, each wrapping a single capability. `enabledPlugins` carries `writing-clearly-and-concisely@agent-toolkit` and nothing else from the 56; the installed tree is one skill directory — `SKILL.md`, `README.md`, `signs-of-ai-writing.md`, and a five-file `elements-of-style/`. The granularity a fork would buy is already on offer upstream.

*And obra did not fork it.* The brief recorded obra as having forked this skill from softaworks into `obra/superpowers-marketplace`, and an earlier draft of this document treated that as evidence the upstream was worth leaving. The chronology refutes it: `obra/the-elements-of-style` was **created 2025-10-14** with `isFork: false` and no parent, while `softaworks/agent-toolkit` was **created 2026-01-19** and its skill first appears 2026-01-18. obra predates softaworks by three months. Both are independent derivations from Strunk's public-domain 1918 text — obra's `plugin.json` states `"license": "Public Domain"` outright — which is precisely why two can exist with neither forking the other. **There is no fork here, no divergence to assess, and no third option.** Depend on softaworks.

*The direction of derivation is the reverse of the brief's.* The two `SKILL.md` files are near-identical in wording — same "When to Use This Skill" list closing on the same bolded *"If you're writing sentences for a human to read, use this skill."*, same three-step "Limited Context Strategy". That is copying, not parallel invention, and obra predates softaworks by three months, so softaworks derived from obra. obra's `"license": "Public Domain"` permits it. The book text is public domain either way; it is the authored wrapper that establishes direction.

*Which to keep: softaworks, as installed.* Two reasons, both content rather than provenance.

- **The split makes the skill's own strategy work.** Both files instruct the agent to dispatch a subagent with "the relevant section" under context pressure. Only softaworks can: its Strunk text is five files of 303 B to 33 KB, roughly 1,000–4,500 tokens each. obra ships one 71 KB `elements-of-style.md` and its own `SKILL.md` warns it *"consumes ~12,000 tokens"* — describing a capability the layout does not support.
- **`signs-of-ai-writing.md` has no counterpart.** At 94 KB it is larger than the Strunk text, and softaworks' overview states the division plainly: *"what to do (Strunk) and what not to do (AI patterns)."* For a vault whose prose is substantially agent-drafted, that half plausibly carries more weight than the 1918 half. Totals: 178 KB against 73 KB.

softaworks' description is also better shaped for invocation — *"Use when writing prose humans will read—"* is a trigger, where obra's *"Apply Strunk's timeless writing rules to ANY prose"* is an instruction.

*The one point against, and the re-audit trigger it implies.* softaworks last pushed 2026-03-05, obra 2026-08-12 — nearly six months quiet. That matters little for a 1918 public-domain text, but `signs-of-ai-writing.md` is the component that decays, since AI writing tells change. **This is the plugin in this survey most likely to fire the material-upstream-change trigger**, and the thing to watch is that file rather than the repository's commit rate.

*A naming detail before installing both.* obra's plugin is `elements-of-style` but its skill is also `writing-clearly-and-concisely` — no plugin collision, but identical skill names, which per #89 means two catalog entries with nothing to resolve them.

**A find for #59 and #69, surfaced by checking the above.** `obra/the-elements-of-style` is a working cross-harness plugin exemplar. One source repository carries generated manifests for eight harnesses — `.claude-plugin/`, `.codex-plugin/`, `.cursor-plugin/`, `.devin-plugin/`, `.hermes-plugin/`, `.kimi-plugin/`, `.opencode/`, `.pi/`, plus `.agents/plugins/marketplace.json` — produced and checksummed by a tool, recorded in `.everyharness/manifest.json` as `"tool": "everyharness@0.7.0"`. That is a maintained, live answer to the exact question #59 asks about serving two harnesses from one source, and it bears on #69's conformance check. Worth reading before either invents a layout.

**`security-guidance` ships no skills, agents or commands** — hooks and nothing else: six registrations invoking a shared entrypoint over roughly 330KB of interdependent Python across 9 modules, plus an Agent SDK bootstrap at SessionStart with a 180-second timeout. Its Stop-hook half has no Codex equivalent; Codex's event set is `pre_tool_use`, `post_tool_use`, `permission_request`, `pre_compact`, `post_compact`, `session_start`, `session_end`, `user_prompt_submit`, `subagent_start`, `subagent_stop` — no main-agent Stop. Keeping it at step 1 avoids vendoring that Python for a Claude-only capability `codex-security` already covers by another mechanism on the other harness.

**`superpowers-developing-for-claude-code` has no bucket and no fork call, because the plugin is not adopted.** Both its skills are step-3 adaptations into `software-development` (see [The obra pair](#the-obra-pair)), so there is no as-is dependency for a bucket to describe and nothing to fork. An earlier draft marked it `required` on the reasoning that the destination is a maintainer product; that is not the bucket test, which asks whether `software-development` runs without it. It does.

Upstream is **dormant**: `pushedAt` 2025-12-03, and main HEAD equals the `v0.3.1` tag equals the installed pin `74afe935` — nine months quiet with no unreleased work. That makes vendoring the easy case rather than the risky one; there is nothing to merge.

### superpowers — fork it

**Nature.** The author's position on as-is adoption is an observation, not a ruling — verbatim: *"I didn't rule that superpowers can't be adopted as-is. I said unfortunately the evidence suggests it is impossible."*

**Rung 1 fails — measured.** `hooks/hooks.json` registers a SessionStart hook on matcher `startup|clear|compact`, and `hooks/session-start` injects `skills/using-superpowers/SKILL.md` verbatim inside `<EXTREMELY_IMPORTANT>` tags. That file routes to the skill being replaced, by qualified name, twice:

- line 22 — *"**Before entering plan mode:** if you haven't already brainstormed, invoke the brainstorming skill first."*
- line 30 — *"`\"Let's build X\"` → superpowers:brainstorming first, then implementation skills."*

So rung 1's cost is not a passive catalog duplicate that a better description could out-compete. It is an always-on injected directive naming the competitor — and once inside, `brainstorming`'s `<HARD-GATE>` and its *"The ONLY skill you invoke after brainstorming is writing-plans"* clause foreclose handing back. The failure is not "picks arbitrarily"; it is "reliably picks the replaced skill, then locks the door."

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

`e.source === "plugin"` returns `"on"` unconditionally; the override map is never reached. The branch above it is not a plugin path — `sPy` is `new Set(["auto-mode-setup"])`, one built-in command. Corroborated twice in the same binary: the `/skills` UI excludes entries where `loadedFrom !== "skills" && loadedFrom !== "commands_DEPRECATED"`, and `/plugin` exposes only `plugin:toggle` and `plugin:install`.

This settles #60's open question, though the question was framed on a borrowed authority. #60 asked whether *"`skillOverrides` cannot patch plugin skills"* had gone stale, citing `docs/superpowers/specs/2026-08-16-foundation-spec.md` §7 — which is **research-vault's** foundation specification, governing that product, not this one. `software-development` inherits no doctrine from it. What settles the question is not that document's standing but the fact itself, verified here against the installed binary: the behaviour is current at 2.1.220. research-vault's spec records the same fact for its own purposes, and its opening warns that its contents *"should not be over generalized"*. Codex is more total, not less: `codex plugin --help` on codex-cli 0.147.0 lists only `add`, `list`, `marketplace`, `remove`, there is no `codex skill` subcommand, and `~/.codex/config.toml` carries no skill-level key.

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

The breakage class is permanent, not one-off: 20 commits since 2026-01-01 touched `superpowers:` strings under `skills/`, `writing-skills/SKILL.md:283` prescribes the qualified form as house style, and such changes **auto-merge without conflict** — so each future one lands silently broken.

**So vendoring cannot stay at rung 3 here.** Copying these skills out requires editing 26 references, which is rung 4 by definition.

This is specific to `superpowers`, not general. Vendoring by itself does not push rung 3 to rung 4 — a byte-identical copy stays at rung 3, because the ladder distinguishes whether the text changed, not how it arrived. It is `superpowers`' 26 cross-references that force the edit.

**Rung 2 — fork — is the answer.** Qualified names are `pluginName:skillName`, independent of marketplace — corroborated live against `superpowers-developing-for-claude-code:developing-claude-code-plugins`, namespaced by plugin name while its marketplace is `superpowers-developing-for-claude-code-dev`. **Keeping `"name": "superpowers"` preserves all 26 references untouched.** And because a fork is a separately distributed plugin with its own root, it is a dependency rather than vendored content — so it never becomes a #63 drift surface in the way 13 copied skill directories would.

Measured by building the fork at pin `44c9b2d6` and merging upstream HEAD `b36e0829` (v6.3.0, five weeks, 415 lines across 13 skill files):

- Patch: **10 files changed, 117 insertions, 1933 deletions** — delete `skills/brainstorming/`, edit two lines of `using-superpowers/SKILL.md`, replace the `AGENTS.md` symlink with a regular file.
- Merge: **exactly two conflicts**, both `DU` on the deleted directory, resolved by `git rm -r`, fully scriptable.
- The one file the fork edits **auto-merged cleanly** even though upstream touched it.

**Upstream health, for the fork call.** `obra` (Jesse Vincent), 279,648 stars, last push 2026-08-29, monthly releases (v6.1.0 06-30, v6.2.0 07-24, v6.3.0 08-12), 100 commits touching `skills/` since 2026-06-01. No `eranroseman` fork exists today. **The machine is pinned at 6.2.0 while v6.3.0 shipped 2026-08-12** — one minor version behind, and v6.3.0 touched 12 skill files.

**Asking upstream instead is a non-starter.** `brainstorming` is the plugin's first manifest keyword and its `defaultPrompt` is *"I've got an idea for something I'd like to build."* — it is the front door obra is selling, not an incidental skill.

**A fourth arrangement, rejected.** Claude Code marketplace entries can declare a plugin's components — the binary carries *"has conflicting manifests: both plugin.json and marketplace entry specify components. Set `strict: true` in marketplace entry or remove component specs from one location."* Since upstream's `.claude-plugin/plugin.json` declares no components, an entry-level `skills` array selecting 13 of 14 would conflict with nothing: curation with no fork and no vendoring. **It dies on Codex**, whose single-path `skills` key (above) cannot express a subset — so it fails the destination's cross-harness requirement.

**Three live defects a fork lets you fix — measured, and each fixed by a different act.**

| Defect | Fixed by |
|---|---|
| Codex's `[marketplaces.superpowers-dev]` is `source_type = "local"`, pointing at `/home/eranr/.claude/plugins/marketplaces/superpowers-dev`, so the Codex install is parasitic on a Claude install having happened first and **cannot reproduce on a fresh machine**. Every other Codex marketplace here is `source_type = "git"`. | Publishing the fork at a **git URL** |
| #56's missing Codex `AGENTS.md`: `git ls-files -s AGENTS.md` returns mode `120000` (a tracked symlink) while `git status --porcelain` reports ` D AGENTS.md` and no file exists on disk. Codex drops the symlink, so 8,873 bytes of plugin-level guidance are silently absent. | The **10-file patch**, which commits it as a regular file |
| Codex's manifest declares `"hooks": {}`, so **superpowers' SessionStart hook does not fire on Codex at all**, even though `hooks/` is copied there. Codex supports `session_start` and sets `CLAUDE_PLUGIN_ROOT`; superpowers simply does not wire it. | **Nothing yet** — the measured patch does not wire it either. A fork makes the fix *possible*; someone still has to author it. Route to #61 |

**Known gaps in this recommendation.** The fork patch is under-scoped as measured: `tests/brainstorm-server/` holds 12 live test files hard-coding `skills/brainstorming/scripts/...`, all orphaned by the deletion. And a fork nobody merges becomes a stale private snapshot — the exact failure `harness-backup` exists to avoid, reintroduced elsewhere. **Without #63's merge-base monitor the fork is strictly worse than step 1**, so that monitor is a precondition of this recommendation rather than a nice-to-have.

**This reverses a clause of [#72](https://github.com/eranroseman/knowledge-harness/issues/72)**, which recorded the process spine as "adopted as-is" while simultaneously vendoring `brainstorming` out of it — two statements that cannot both hold at plugin granularity. Recorded as a dated reversal rather than left contradicted, per the precedent [#77](https://github.com/eranroseman/knowledge-harness/issues/77) set when it reversed clauses of [#89](https://github.com/eranroseman/knowledge-harness/issues/89). Everything else in #72 stands: the two-vendor split, mattpocock's process skills not adopted, `grilling` adopted unmodified with its mute removed, `brainstorming` vendored as `writing-specs`, the reclassifications, and the sharing test. **Only the adoption mechanism changes.** The reversal is this ticket's to make, drawn from the measurements above — not an author ruling.

### mattpocock's skills

**18 installed**, standalone via `~/.agents/.skill-lock.json`, not as a plugin.

- All adopted skills are **rung 3, vendored** into whichever product needs them.

**To `shared-skills`:** `grilling`, `research`, `handoff`, `teach`, `to-questionnaire`, `wait-what`, `wayfinder`, `wizard`, `writing-for-agents`.
- **To `software-development`:** `codebase-design`, `prototype`, `resolving-merge-conflicts`, `improve-codebase-architecture`, `triage`.
- **Rung 4, adapt:** `domain-modeling`, `setup-matt-pocock-skills`.
- **Not adopted:** `grill-with-docs`, `to-tickets`, per #72's process-skill ruling.

**Why not fork `mattpocock/skills`, given rung 2 outranks rung 3?** Four reasons, and the first is decisive.

- **Forking buys nothing here.** The whole justification for the `superpowers` fork is namespace preservation, and it does not apply: `grep -ro 'mattpocock-skills:'` across the installed set returns **zero**. Every cross-reference is a bare name — `grilling` is referenced by `improve-codebase-architecture`, `triage` and `wayfinder`; `domain-modeling` by three; `prototype` by two — and bare names survive relocation. There is no namespace to preserve.
- **Two forks would collide on the name.** The adopted skills split across two distributables, nine to `shared-skills` and five to `software-development`, and one fork cannot be two products. Two forks cannot both be `mattpocock-skills`, so at least one must be renamed — paying the rename cost for a namespace benefit that does not exist.
- **Doubled merge burden on a live upstream.** Two forks tracking one active repository means two merges per upstream change, each maintaining a different deletion set — 28 skills deleted in one, 32 in the other — indefinitely.
- **Recategorisation would become a two-repository transaction.** Moving one skill between the productivity and engineering sides becomes a delete in one fork and an add in the other, in lockstep. Under vendoring it is a file move.

A fifth consideration is structural: `shared-skills` holds **plugin components and nothing else** (author, 2026-08-30, clarifying #77 — whose "nothing else" was aimed at `terminology.md` and glossaries, not at components). A fork of someone else's repository minus 28 skills is not a component set, and it could never cleanly hold an authored or non-mattpocock component later.

**A defect in the sharing split, found by mapping those references.** The bare-name calls are fine within a product but not across the boundary, and one crosses it: **`wayfinder` is shared, and its Prototype ticket type instructs the agent to call `prototype`, which is `software-development`-only.** A researcher installing `research-vault` plus `shared-skills` gets `wayfinder` without `prototype`, and that ticket type silently has nothing to invoke. The same shape threatens `domain-modeling`, which `wayfinder` also calls — and that is the mechanical reason it is genuinely split rather than a matter of taste. Route to #89's mechanism or to whichever ticket owns the final shared roster; it is not resolvable inside a per-skill verdict.

Note this is a **product-boundary** problem, not a component-kind one. A skill's own agents, hooks and commands travel with it into `shared-skills`, which holds plugin components; what does not travel is a call to a skill assigned to the *other* product.

Six were independently hash-matched against exact upstream commits and are **pristine but stale** — `domain-modeling` @ `54bc6b6`, `triage` @ `6a34259e`, `writing-for-agents` @ `4aaccb58`, `setup-matt-pocock-skills` @ `c66bdee`, `grilling` @ `86cba45f`, `wayfinder` @ `6a34259e`.

**19 not installed — all recommended not adopted.** `ask-matt`, `code-review`, `diagnosing-bugs`, `implement`, `tdd`, `to-spec`, `grill-me`, `claude-handoff`, `implement-spec`, `loop-me`, `retro`, `setup-ts-deep-modules`, `writing-beats`, `writing-fragments`, `writing-shape`, `git-guardrails-claude-code`, `migrate-to-shoehorn`, `scaffold-exercises`, `setup-pre-commit`.

The upstream roster is 37 skills — engineering 18, productivity 7, in-progress 8, misc 4 — certified by mechanical set-diff against `find skills -name SKILL.md`, empty in both directions. Adoption of something the author currently lives without required naming a concrete gap it fills; none did. The only dissent ran the other way: two of the four passes argued `diagnosing-bugs`, `tdd` and the `writing-*` trio were declined without pricing an adaptation.

### The obra pair

`working-with-claude-code` and `developing-claude-code-plugins` are each installed **twice** — inside the `superpowers-developing-for-claude-code` plugin, and standalone via the lockfile from the same upstream. Both live simultaneously.

**Both are rung 4, both to `software-development`, neither shared.** They separate on *consumer* rather than depth. `developing-claude-code-plugins` is an authoring workflow whose artefacts are `.claude-plugin/plugin.json`, `marketplace.json`, `hooks.json` and git tags. `working-with-claude-code` is a runtime reference whose nine "When to Use" triggers are all harness extension, configuration and troubleshooting. A researcher doing evidence work in a vault produces neither class of artefact, so the sharing test excludes both — and it excludes them for different reasons, which is why they were judged separately rather than as a pair.

**What forces rung 4 rather than rung 3 — measured, and it is the same finding that decides the dedupe.** Each install shape is broken in a way the other one masks:

- The **plugin's** copy of `working-with-claude-code` hardcodes standalone paths — `SKILL.md:119` reads `path: ~/.claude/skills/working-with-claude-code/references/` and `SKILL.md:132` invokes `node ~/.claude/skills/working-with-claude-code/scripts/update_docs.js`. `${CLAUDE_PLUGIN_ROOT}` appears **zero** times in the file. Neither path resolves from a plugin install; they resolve today only because the standalone copy coincidentally exists.
- The **standalone** copy of `developing-claude-code-plugins` references `examples/simple-greeter-plugin/` and `examples/full-featured-plugin/` in three places, but those directories live at **plugin root**, not inside the skill folder. The lockfile install therefore ships no examples at all.

**So the dedupe answer is: keep both for now, drop both later.** An earlier draft recommended keeping the plugin and dropping the lockfile entries. That is wrong on this evidence — removing either copy today breaks the other. The correct sequence is that `software-development` ships the adapted copies first, at which point both current installs become redundant together. **The adaptation is what makes deduplication safe, not a precondition of it.** Routes to #60 and #62 as one motion.

**A drift asymmetry for #63.** `working-with-claude-code`'s true upstream is not obra: its 42 reference files are generated from `docs.claude.com` by the bundled `scripts/update_docs.js`, and they are stale — missing `skillOverrides`, plugin `dependencies`, and `allowCrossMarketplaceDependenciesOn`, all three of which this programme now relies on. Its drift question is "have Anthropic's docs moved", not "has obra committed", and a monitor watching the obra pin would report clean while the content rots.

**Adaptations for #60**, beyond the provenance header both need: rewrite the two hardcoded paths in `working-with-claude-code` to `${CLAUDE_PLUGIN_ROOT}`-relative form and re-run `update_docs.js` to refresh the 42 references; co-locate or re-path the two `examples/` directories for `developing-claude-code-plugins`, and subordinate its Phase 1 (Plan) and Phase 6 (Release) to `superpowers:writing-plans` and `superpowers:finishing-a-development-branch` so the spine settled in #72 is not duplicated.

### The four harness-backup skills

Recommendation only — the owning tickets decide.

| Skill | Rung | Home | Owning ticket |
|---|---|---|---|
| `consistency-audit` | 3 — vendor | **`shared-skills`** | #79 |
| `rethink-audit` | 3 — vendor | `software-development` | #73 |
| `rethink` | **not adopted — drop** | — | #73 |
| `finding-duplicate-functions` | 4 — adapt | `software-development` | #60 (the clearest vendoring case on the machine) |

**`consistency-audit` is shared, correcting an earlier verdict.** Its own description is *"contradictions, duplication, drifted terms, stale claims"* — what a research vault accumulates at least as much as a code repository does. The earlier `software-development`-only call was reached from framing vocabulary (*"read a **repository** whole"*) rather than capability, the same error that produced the `wayfinder`/`prototype` finding above. The skill degrades gracefully by design: *"Most repositories have none of these. When one is absent, proceed with the defaults and say nothing."*

Its subagent travels with it. `consistency-audit` hard-dispatches `consistency-audit-inspector` at `SKILL.md:78` (*"two independent readers over every slice"*) and again at `:116` (*"instructed to refute"*), and that agent lives outside the skill directory at `~/harness-backup/claude/agents/`. Under a reading of #77 as *skills* and nothing else this would have blocked the assignment; under the author's clarification that `shared-skills` holds **plugin components**, an agent qualifies and the blocker dissolves. #51 separately flagged this agent as sitting outside the drift detector's watched set and deferred it to #78 — that remains open and is now more load-bearing, since the agent becomes shipped rather than local.

**`rethink` is dropped, on duplication rather than principle.** Its entire body is one sentence: *"Run a `/rethink-audit` pass on a fresh design question: no implementation exists, so work through `design:` and finish at `trade-offs:`."* `rethink-audit` already carries that instruction at line 60: *"On a fresh design question there is no implementation: run through `design:`, then `trade-offs:`."* Near-verbatim. It is not a wrapper adding a parameterisation — it restates a line already inside the skill it delegates to.

This answers #73's second question differently from how that ticket frames it. The front door does not absorb `/rethink`, and it does not survive as a distinct no-dialog entry point: **`rethink-audit` absorbed it already.** It also means `rethink-audit` needs no adaptation to cover the fresh-design case, which keeps it at rung 3 rather than moving it to rung 4.

**`rethink-audit` is `software-development`, but weakly.** Its method reconstructs `requires:` "from its boundary — signatures, call sites, tests" and reads "the current implementation" at `gap:`, with migration cost as the frame — that needs code. The usage evidence argues wider: of the seven audits in `docs/research/rethink-audits/`, several are not code at all (`controller-protocol`, `development-process`, `glossary-and-adr-triage`, `coding-companion-plugin-layering`). All remain engineering-domain, so the verdict holds, but it is a borderline call rather than a clean one. Both `rethink` and `rethink-audit` ship `agents/openai.yaml`, so they are already cross-harness ready.

On `rethink`, the author has ruled these land in either `software-development` or `shared-skills`, and that **both** the public `eranroseman/rethink` repository and the harness-backup copies are deleted. Recorded on #73.

## The six sharing verdicts this ticket owed

Four were deferred here by #89 — `domain-modeling`, `triage`, `writing-for-agents`, `setup-matt-pocock-skills`. Two more were left unforced by earlier tickets — `working-with-claude-code` and `superpowers`. All six rest on the skill bodies rather than on folder names.

| Skill | Verdict |
|---|---|
| `writing-for-agents` | `shared-skills` |
| `triage` | `software-development` |
| `working-with-claude-code` | `software-development` |
| `superpowers` | `software-development` — meaning **it is `software-development` that depends on it and `research-vault` that does not**. The fork remains a separate plugin with its own root; this axis assigns which product needs the capability, not where the files sit |
| `domain-modeling` | **genuinely split**, and now for a mechanical reason rather than a judgement: `wayfinder` is shared and calls it, while `improve-codebase-architecture` and `triage` are `software-development` and call it too. Assign it to either side alone and a caller on the other side dangles |
| `setup-matt-pocock-skills` | **no bucket** — it is a rung-4 template rather than a capability either product ships |

`working-with-claude-code` is the one reversal here. It was argued during the grilling as shared, on the grounds that it documents the runtime both products run on. Two passes placed it with engineering instead: its depth is hook wiring, MCP server setup and settings resolution, which is maintainer work rather than vault work, and it does not separate from `developing-claude-code-plugins` the way the shared reading required.

## Handoff to #60

Every asset landing on rung 4, copy-consumable.

| Asset | What must change |
|---|---|
| `brainstorming` → `writing-specs` | Rename; correct the description, which promises open-ended ideation while the body is a one-way funnel from idea to committed spec with a mandatory approval gate; decide the Visual Companion; decide the base version |
| `domain-modeling` | Resolve the split; adaptation scope for #60 to set |
| `setup-matt-pocock-skills` | Adapt as the template for #62's setup mechanism, per #85 |
| `working-with-claude-code` | Adapt, plus the dedupe above |
| `developing-claude-code-plugins` | Same |
| `finding-duplicate-functions` | Provenance header against `obra/superpowers-lab`; the local copy is a substantial rewrite, shell replaced with Python |

**The list shrank because of the fork.** Earlier passes marked `systematic-debugging`, `test-driven-development`, `writing-plans`, `writing-skills` and `using-superpowers` as rung-4 adaptations. Those were artifacts of the vendoring branch — a fork keeps the namespace, so none needs adaptation. That collapse is the fork's clearest practical benefit.

**Two decisions #60 must make knowingly.**

*The Visual Companion is separable but not free.* It is 1,730 lines — `scripts/server.cjs` 723, `scripts/frame-template.html` 213, `scripts/start-server.sh` 209, `scripts/helper.js` 167, `scripts/stop-server.sh` 120, plus `visual-companion.md` 298 — within a `brainstorming` directory totalling 1,930 lines across 8 files. Nothing outside that directory references it, so dropping it costs one file deletion, one directory deletion and about 19 lines from the skill body. But removing those 19 lines means *"internals untouched"*, which is what #72 specified, no longer describes the vendoring. Note also that the companion loads a logo from an external site carrying the Superpowers version, opt-out via `SUPERPOWERS_DISABLE_TELEMETRY`.

*The base version matters.* Upstream HEAD replaced `brainstorming` with a three-path Spike/Bounded/Architectural router — 117 changed lines — **after** the 6.2.0 text #72 judged. Vendoring from the pin ships a skill already a generation behind. Vendor from HEAD, freeze deliberately, or place `writing-specs` under #63's drift watch as a tracked adaptation.

## Handoff to other tickets

**#62 — hard sequencing, and a migration.** The fork's edited bootstrap points at `software-development:writing-specs`. Until that ships, every session injects a route, inside `<EXTREMELY_IMPORTANT>` tags, to a skill that does not exist. `writing-specs` must land before or with the cutover.

The cutover must also uninstall first on both harnesses, because the fork keeps the plugin name and so collides with the installed copy. Two installs must be migrated, not one: `installed_plugins.json` carries a **project-scope entry for `/home/eranr/memoria-vault`** at `gitCommitSha` `3dcbd5c4…` while the user-scope entry has `44c9b2d6…`, both naming the **same** `installPath`. Easy to miss, and it establishes that install path does not imply pin — which #63 and #78 should know independently of this migration.

**#63 — two additions.** Watch upstream HEAD against the fork's merge-base, not just the fork against the installed cache; per the known gaps above, this is a precondition of the fork recommendation rather than an enhancement. And catch **unqualified** references: upstream already added `skill_view("brainstorming")` to `using-superpowers/references/hermes-tools.md:31`, which auto-merges clean and is invisible to a `grep superpowers:brainstorming`.

**#61 — a live constraint, not a blank slate.** A SessionStart injection already fires every startup/clear/compact from the forked superpowers, carrying the skill-invocation discipline. #61 must decide whether `software-development`'s own hook composes with that or duplicates it; Claude Code merges hooks from multiple plugins without dedup. The two edited routing lines in `using-superpowers/SKILL.md` are a supported seam and they merge cleanly. #61 also inherits the unwired Codex hook from the defect table above.

**#64 — two.** The declared-asset policy gap below, and: **`finding-duplicate-functions` is absent from `harness-backup`'s README entirely**, so a fresh-machine restore silently omits it.

**#81 — `to-spec` is mattpocock's PRD skill, renamed.** `CHANGELOG.md:181` — *"`to-prd` is renamed to `to-spec`"*; `docs/engineering/to-spec.md:38` — *"Where did `/to-prd` go? It is this skill, renamed in v1.1."* So #81's premise that no vendor's roster contains one is wrong in letter. It is worth more as a cited failure mode than as a donor, because upstream documents its own defect at `docs/engineering/to-spec.md:57`: *"The template leans hard on user stories, which is the wrong shape for architectural work: you end up writing stories nobody asked for around decisions that are really about interfaces and invariants."* Its template divides along exactly the line #81 must draw — product: Problem Statement, Solution, User Stories; engineering: Implementation Decisions, Testing Decisions; shared: Out of Scope, Further Notes. Also minable: `triage/AGENT-BRIEF.md`, 207 lines, MIT, already installed.

**#78 — an offered requirement.** See the cache anomaly below.

## The five anomalies #75 carried

1. **The orphaned-cache count in the ticket body is wrong.** Of 16 directories under `~/.claude/plugins/cache/`, nine are enabled pins. Of the remaining seven: three are superseded versions of still-enabled plugins (routine garbage-collection lag from a batch update on 2026-08-10); three are **true orphans** with no enabled successor — `interface-design`, `pr-review-toolkit`, `frontend-design`, where the ticket named only the first; and one, `caveman/caveman/17f9f2ec2377`, is unreferenced **and unmarked**, with a larger roster than the pin. Filed as [#95](https://github.com/eranroseman/knowledge-harness/issues/95) and ruled out of scope for map #53 as machine hygiene.

   *The finding for #78:* the client's own `.orphaned_at` marker is **not** a complete signal — six of the seven carry it and one does not — so a doctor check that trusts it misses exactly the case most warranting a human look. Set subtraction against `installPath` is the reliable test. Offered as an inherited requirement, to take or decline.

2. **The double-installed obra skills** — decided under [The obra pair](#the-obra-pair) above.

3. **The dormant `rethink` marketplace** routes to #73 as one motion with the placement and deletion calls, per #51's deliberate bundling — deleting the upstream repository makes the registration dead by definition.

4. **The empty `claude-plugins-official` marketplace** is out of scope, filed with #95. It is a different registration from `claude-code-plugins`, which supplies the live `security-guidance` and must not be removed alongside it.

5. **The declared-asset policy gap was mislocated in the ticket body.** It is not in this repository's `AGENTS.md`; it lives in the global `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`, both covering only the `npx skills add -g` path with no declared-asset surface for native installs. Routed to #64 by the author, on the reasoning that a hand-maintained table is the weakest tier under this repo's own *eliminate > mechanism > rule > prose* ordering and goes stale on the next install.

## Appendix: method

Four adversarially-verified survey passes. Each assessed on evidence read off disk or fetched from upstream, then was refuted by an independent agent instructed to default to rejection where a claim rested on a description rather than a file body. Where the text above cites "two of the four passes", that is the denominator.

Sources read fresh rather than inherited from earlier tickets: `~/.claude/settings.json`, `~/.claude/plugins/installed_plugins.json`, `~/.claude/plugins/known_marketplaces.json`, `~/.claude/plugins/cache/`, `~/.codex/config.toml`, `~/.codex/plugins/cache/`, `~/.agents/.skill-lock.json`, `~/harness-backup/claude/skills/`, and the installed Claude Code binary at `~/.local/share/claude/versions/2.1.220`.

Where a claim decided a branch it was re-verified by hand outside the surveys — the override resolver, the cross-reference count, the upstream licence and repository statistics, and the Codex manifest. Three figures the surveys reported were corrected that way: the cross-reference count (24 and 25 were both reported), the upstream licence (`gh repo view` reported none; the licence endpoint confirms MIT), and the orphaned-cache count.
