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

1. **Use the whole plugin as-is.** A plugin is all its components — skills, hooks, subagents, slash commands, MCP servers.
2. **Use selected components as-is** — any subset of those kinds, unmodified.
3. **Adapt a component** — a modified copy carrying provenance.
4. **Write one.**

Steps 2–4 read *component*, not *skill*. That is not cosmetic: the difference between step 3 and step 4 is **provenance**, so confining step 3 to skills would force any adapted hook, subagent or command to be filed as step 4 — silently stripping the provenance obligation and leaving #63 nothing to watch. #61's lean-router SessionStart hook is a live case.

**The buckets.** Anything clearing the as-is gate is exactly one of **required** (the plugin does not work without it), **recommended** (works without it, but a user should have it), or **unrelated** (no relationship to either product; personal harness furniture).

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

Plugin-level disposition is the operative call. **Where a plugin is step 1, all its components come across and per-skill detail is informational only.**

| Plugin | Harness | Step | Bucket | Fork call |
|---|---|---|---|---|
| `superpowers` | both | **3 — fork** | required | **fork** |
| `superpowers-developing-for-claude-code` | Claude | 3 — adapt components | required | n/a — plugin not adopted |
| `obsidian` | both | 1 — as-is | recommended | depend upstream |
| `writing-clearly-and-concisely` | both | 1 — as-is | recommended | **three-way, see below** |
| `diataxis-skills` | both | 1 — as-is | recommended | depend upstream |
| `codex` (openai-codex bridge) | Claude | 1 — as-is | recommended | depend upstream |
| `codex-security` | Codex | 1 — as-is | recommended | depend upstream |
| `security-guidance` | Claude | 1 — as-is | recommended | depend upstream |
| `ponytail` | both | 1 — as-is | recommended | depend upstream |
| `caveman` | both | 1 — as-is | **unrelated** *(unconfirmed)* | depend upstream |

Four rows need their reasoning stated.

**`caveman` — unconfirmed, and genuinely two-sided.** *For `unrelated`:* under the necessity test nothing in `software-development` invokes it, and a public plugin recommending an output-style mode recommends taste rather than capability. *For `recommended`:* its core mode is general compressed communication that a researcher benefits from identically, and only two of its skills — `caveman-commit` and `caveman-review` — are git-specific. Two of the four survey passes split on exactly this. It stays installed either way; the bucket only decides whether the README names it.

**`writing-clearly-and-concisely` — the fork call is a three-way, not two.** obra already forked this skill from `softaworks/agent-toolkit` into `obra/superpowers-marketplace`, a marketplace already consumed here for `superpowers`. So "depend on someone else's existing fork" is available alongside depending on softaworks directly and forking independently. It is also the plugin here most likely to hit the re-audit trigger: a single skill from a small upstream, where obra's fork is already evidence someone judged that upstream worth leaving.

**`security-guidance` ships no skills, agents or commands** — hooks and nothing else: six registrations invoking a shared entrypoint over roughly 330KB of interdependent Python across 9 modules, plus an Agent SDK bootstrap at SessionStart with a 180-second timeout. Its Stop-hook half has no Codex equivalent; Codex's event set is `pre_tool_use`, `post_tool_use`, `permission_request`, `pre_compact`, `post_compact`, `session_start`, `session_end`, `user_prompt_submit`, `subagent_start`, `subagent_stop` — no main-agent Stop. Keeping it at step 1 avoids vendoring that Python for a Claude-only capability `codex-security` already covers by another mechanism on the other harness.

**`superpowers-developing-for-claude-code` has no fork call because the plugin is not adopted.** Both of its skills are step-3 adaptations into `software-development` (see [The obra pair](#the-obra-pair)), so nothing is depended on and there is nothing to fork.

### superpowers — fork it

**Nature.** The author's position on as-is adoption is an observation, not a ruling — verbatim: *"I didn't rule that superpowers can't be adopted as-is. I said unfortunately the evidence suggests it is impossible."*

**Step 1 fails — measured.** `hooks/hooks.json` registers a SessionStart hook on matcher `startup|clear|compact`, and `hooks/session-start` injects `skills/using-superpowers/SKILL.md` verbatim inside `<EXTREMELY_IMPORTANT>` tags. That file routes to the skill being replaced, by qualified name, twice:

- line 22 — *"**Before entering plan mode:** if you haven't already brainstormed, invoke the brainstorming skill first."*
- line 30 — *"`\"Let's build X\"` → superpowers:brainstorming first, then implementation skills."*

So step 1's cost is not a passive catalog duplicate that a better description could out-compete. It is an always-on injected directive naming the competitor — and once inside, `brainstorming`'s `<HARD-GATE>` and its *"The ONLY skill you invoke after brainstorming is writing-plans"* clause foreclose handing back. The failure is not "picks arbitrarily"; it is "reliably picks the replaced skill, then locks the door."

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

This settles #60's open question about whether the ruling in the foundation specification (`docs/superpowers/specs/2026-08-16-foundation-spec.md`, §7) that *"`skillOverrides` cannot patch plugin skills"* had gone stale. It has not. Codex is more total, not less: `codex plugin --help` on codex-cli 0.147.0 lists only `add`, `list`, `marketplace`, `remove`, there is no `codex skill` subcommand, and `~/.codex/config.toml` carries no skill-level key.

**Step 2 fails — measured.** The wanted skills carry **26** hard-coded `superpowers:`-qualified cross-references across 9 files, on 25 lines (one line carries two), verified by `grep -ro` against the installed cache. **None sits inside `skills/brainstorming/`**, so every one survives that directory's deletion and every one breaks under vendoring.

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

**So the choice was never step 1 versus step 2.** Taking these skills individually requires editing them, which is step 3 by definition.

Note this is specific to `superpowers`, not general. Vendoring by itself does not turn step 2 into step 3 — a byte-identical vendored copy is still step 2, because the ladder distinguishes whether the text changed, not how it arrived. It is `superpowers`' 26 cross-references that force an edit and therefore force step 3.

**Why forking beats vendoring.** Qualified names are `pluginName:skillName`, independent of marketplace — corroborated live against `superpowers-developing-for-claude-code:developing-claude-code-plugins`, namespaced by plugin name while its marketplace is `superpowers-developing-for-claude-code-dev`. **Keeping `"name": "superpowers"` preserves all 26 references untouched.** And because a fork is a separately distributed plugin with its own root, it is a dependency rather than vendored content — so it never becomes a #63 drift surface in the way 13 copied skill directories would.

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

- **To `shared-skills`:** `grilling`, `research`, `handoff`, `teach`, `to-questionnaire`, `wait-what`, `wayfinder`, `wizard`, `writing-for-agents`.
- **To `software-development`:** `codebase-design`, `prototype`, `resolving-merge-conflicts`, `improve-codebase-architecture`, `triage`.
- **Step 3:** `domain-modeling`, `setup-matt-pocock-skills`.
- **Not adopted:** `grill-with-docs`, `to-tickets`, per #72's process-skill ruling.

Six were independently hash-matched against exact upstream commits and are **pristine but stale** — `domain-modeling` @ `54bc6b6`, `triage` @ `6a34259e`, `writing-for-agents` @ `4aaccb58`, `setup-matt-pocock-skills` @ `c66bdee`, `grilling` @ `86cba45f`, `wayfinder` @ `6a34259e`.

**19 not installed — all recommended not adopted.** `ask-matt`, `code-review`, `diagnosing-bugs`, `implement`, `tdd`, `to-spec`, `grill-me`, `claude-handoff`, `implement-spec`, `loop-me`, `retro`, `setup-ts-deep-modules`, `writing-beats`, `writing-fragments`, `writing-shape`, `git-guardrails-claude-code`, `migrate-to-shoehorn`, `scaffold-exercises`, `setup-pre-commit`.

The upstream roster is 37 skills — engineering 18, productivity 7, in-progress 8, misc 4 — certified by mechanical set-diff against `find skills -name SKILL.md`, empty in both directions. Adoption of something the author currently lives without required naming a concrete gap it fills; none did. The only dissent ran the other way: two of the four passes argued `diagnosing-bugs`, `tdd` and the `writing-*` trio were declined without pricing an adaptation.

### The obra pair

`working-with-claude-code` and `developing-claude-code-plugins` are each installed **twice** — inside the `superpowers-developing-for-claude-code` plugin, and standalone via the lockfile from the same upstream. Both live simultaneously. Both are step 3.

**Recommended dedupe — keep the plugin, drop the lockfile entries. Unconfirmed.** Both are step-3 adaptations regardless, so the lockfile copy is the one with no future; and since `skillOverrides` reaches lockfile skills but *not* plugin skills, keeping the muteable copy while dropping the unmuteable one would be backwards.

Cost of leaving both live: two catalog entries with identical descriptions, each spending the per-entry skill-listing character budget (1,536 characters per entry, governed by `skillListingBudgetFraction`), and bare `/name` stops resolving.

### The four harness-backup skills

Recommendation only — the owning tickets decide. All four sit with `software-development` on the sharing axis.

| Skill | Step | Owning ticket |
|---|---|---|
| `finding-duplicate-functions` | 3 — adapt | #60 (the clearest vendoring case on the machine) |
| `consistency-audit` | 2 — as-is | #79 |
| `rethink` | 2 — as-is | #73 |
| `rethink-audit` | 2 — as-is | #73 |

On `rethink`, the author has ruled these land in either `software-development` or `shared-skills`, and that **both** the public `eranroseman/rethink` repository and the harness-backup copies are deleted. Recorded on #73.

## The six sharing verdicts this ticket owed

Four were deferred here by #89 — `domain-modeling`, `triage`, `writing-for-agents`, `setup-matt-pocock-skills`. Two more were left unforced by earlier tickets — `working-with-claude-code` and `superpowers`. All six rest on the skill bodies rather than on folder names.

| Skill | Verdict |
|---|---|
| `writing-for-agents` | `shared-skills` |
| `triage` | `software-development` |
| `working-with-claude-code` | `software-development` |
| `superpowers` | `software-development` — meaning **it is `software-development` that depends on it and `research-vault` that does not**. The fork remains a separate plugin with its own root; this axis assigns which product needs the capability, not where the files sit |
| `domain-modeling` | **genuinely split** — and load-bearing for two adopted skills, `improve-codebase-architecture` and `wayfinder`, that reference it, so it cannot simply be dropped from either side |
| `setup-matt-pocock-skills` | **no bucket** — it is a step-3 template rather than a capability either product ships |

`working-with-claude-code` is the one reversal here. It was argued during the grilling as shared, on the grounds that it documents the runtime both products run on. Two passes placed it with engineering instead: its depth is hook wiring, MCP server setup and settings resolution, which is maintainer work rather than vault work, and it does not separate from `developing-claude-code-plugins` the way the shared reading required.

## Handoff to #60

Every asset landing on step 3, copy-consumable.

| Asset | What must change |
|---|---|
| `brainstorming` → `writing-specs` | Rename; correct the description, which promises open-ended ideation while the body is a one-way funnel from idea to committed spec with a mandatory approval gate; decide the Visual Companion; decide the base version |
| `domain-modeling` | Resolve the split; adaptation scope for #60 to set |
| `setup-matt-pocock-skills` | Adapt as the template for #62's setup mechanism, per #85 |
| `working-with-claude-code` | Adapt, plus the dedupe above |
| `developing-claude-code-plugins` | Same |
| `finding-duplicate-functions` | Provenance header against `obra/superpowers-lab`; the local copy is a substantial rewrite, shell replaced with Python |

**The list shrank because of the fork.** Earlier passes marked `systematic-debugging`, `test-driven-development`, `writing-plans`, `writing-skills` and `using-superpowers` as step-3 adaptations. Those were artifacts of the vendoring branch — a fork keeps the namespace, so none needs adaptation. That collapse is the fork's clearest practical benefit.

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
