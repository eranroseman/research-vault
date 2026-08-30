# Installed asset disposition survey

**Date:** 2026-08-30
**Ticket:** [#75 — Installed plugin/skill disposition](https://github.com/eranroseman/knowledge-harness/issues/75), a `wayfinder:grilling` ticket on map [#53](https://github.com/eranroseman/knowledge-harness/issues/53)
**Status:** recommendation. The author has ruled on the framing questions recorded below; the per-asset dispositions are proposals pending sign-off.
**Scope:** every plugin and skill installed on this machine across Claude Code and Codex, plus the full upstream `mattpocock/skills` roster including skills not installed here.

Prior survey in this series: [2026-08-28 alteration-inventory sweep](2026-08-28-alteration-inventory-sweep.md), which diffed every enabled plugin against its pinned commit. This one asks a different question — not "has it drifted" but "what do we do with it".

## Method

Four adversarially-verified survey passes, each assessing on evidence read off disk or fetched from upstream, then refuted by an independent agent instructed to default to rejection where a claim rested on a description rather than a file body. Sources read fresh rather than copied from earlier tickets: `~/.claude/settings.json`, `~/.claude/plugins/installed_plugins.json`, `~/.claude/plugins/known_marketplaces.json`, `~/.claude/plugins/cache/`, `~/.codex/config.toml`, `~/.codex/plugins/cache/`, `~/.agents/.skill-lock.json`, `~/harness-backup/claude/skills/`, and the installed Claude Code binary at `~/.local/share/claude/versions/2.1.220`.

Where a claim decided a branch, it was re-verified by hand outside the surveys. Those re-verifications are marked below.

## The disposition axis, as the author fixed it

The ticket's original axis was adopt-as-is / modify-import / unrelated. The author replaced it on 2026-08-30 with a preference ladder, in strict order:

1. **Use the whole plugin as-is.** A plugin is all its components together — skills, hooks, subagents, slash commands, MCP servers.
2. **Use selected components as-is** — any subset of those component kinds, unmodified.
3. **Adapt a component** — a modified copy carrying provenance.
4. **Write one.**

Anything clearing the as-is gate lands in exactly one bucket: **required** (the plugin does not work without it), **recommended** (works without it), or **unrelated** (no relationship to either product).

Two further rulings from the same session. **Fork policy is per-plugin with no default** — every fork-or-depend call rests on its own upstream evidence, gathered once at adoption rather than re-audited on a schedule. **Distribution of the recommended bucket is deferred** to its own ticket rather than decided here; a README link is the interim position, and a two-package split (dependencies-only plus a bundle) waits until the recommended list exists and is long enough to justify one.

The first function of `software-development` is to be the single home for the non-as-is assets, so they are managed in one designated location rather than per repository.

## The superpowers decision

**Recommendation: fork `obra/superpowers` into the author's own marketplace, delete `brainstorming` there, and depend on the fork from both harnesses.**

**Nature: the findings below are measured; the fork is decided by #75.** The author's position on as-is adoption is an observation rather than a ruling — verbatim: *"I didn't rule that superpowers can't be adopted as-is. I said unfortunately the evidence suggests it is impossible."* The distinction is load-bearing and the foundation spec's status vocabulary requires naming it: a measurement is overturnable by better evidence, a ruling is not. So what follows are measurements of the installed artefacts, and the fork is a conclusion drawn from them — reopenable if the artefacts change.

The conclusion reverses a clause of [#72](https://github.com/eranroseman/knowledge-harness/issues/72), which recorded the process spine as "adopted as-is" while simultaneously vendoring `brainstorming` out of it — two statements that cannot both hold at plugin granularity. Recorded as a dated reversal rather than left contradicted, per the precedent [#77](https://github.com/eranroseman/knowledge-harness/issues/77) set when it reversed clauses of [#89](https://github.com/eranroseman/knowledge-harness/issues/89). The reversal is #75's, not an author ruling.

### Why ladder step 1 fails

`hooks/hooks.json` registers a SessionStart hook on matcher `startup|clear|compact`, and `hooks/session-start` injects `skills/using-superpowers/SKILL.md` verbatim, wrapped in `<EXTREMELY_IMPORTANT>` tags. That file routes to the skill being replaced, by qualified name, twice:

- line 22 — *"**Before entering plan mode:** if you haven't already brainstormed, invoke the brainstorming skill first."*
- line 30 — *"`\"Let's build X\"` → superpowers:brainstorming first, then implementation skills."*

So the cost of step 1 is not a passive catalog duplicate that a better description could out-compete. It is an always-on injected instruction naming the competitor, followed — once inside `brainstorming` — by a `<HARD-GATE>` and the clause *"The ONLY skill you invoke after brainstorming is writing-plans"*, which forecloses handing back. The failure mode is not "picks arbitrarily"; it is "reliably picks the replaced skill, then locks the door".

**It cannot be muted, and this was verified by hand rather than inferred.** Claude Code 2.1.220's resolver:

```js
function jFe(e) {
  if ((e.type === "local-jsx" || e.type === "local") && sPy.has(e.name))
    return eo().skillOverrides?.[e.name] === "off" ? "off" : "on";
  if (e.type !== "prompt" || e.source === "plugin") return "on";
  ...
}
```

`e.source === "plugin"` returns `"on"` unconditionally; the `skillOverrides` map is never consulted. The preceding branch is not a plugin path — `sPy` is `new Set(["auto-mode-setup"])`, a single built-in command. Corroborated twice in the same binary: the `/skills` management UI skips entries where `loadedFrom !== "skills" && loadedFrom !== "commands_DEPRECATED"`, and the `/plugin` UI exposes only `plugin:toggle` and `plugin:install` with no per-component action.

This settles [#60](https://github.com/eranroseman/knowledge-harness/issues/60)'s open question about whether the foundation spec §7 ruling had gone stale. It has not. Recorded there in full.

Codex is worse, not better: `codex plugin --help` on codex-cli 0.147.0 lists only `add`, `list`, `marketplace`, `remove`; there is no `codex skill` subcommand and no skill-level key anywhere in `~/.codex/config.toml`.

### Why ladder step 2 fails

The wanted skills carry **26** hard-coded `superpowers:`-qualified cross-references across 9 files — 25 lines, one of which carries two — verified by `grep -ro` against the installed cache. None is inside `skills/brainstorming/`, so every one survives that directory's deletion and every one breaks under vendoring. Per file: `subagent-driven-development/SKILL.md` 6, `writing-plans/SKILL.md` 4, `writing-skills/SKILL.md` 4, `executing-plans/SKILL.md` 3, `systematic-debugging/SKILL.md` 2, `using-superpowers/SKILL.md` 2, `using-superpowers/references/gemini-tools.md` 2, `test-driven-development/writing-good-tests.md` 1, `writing-skills/testing-skills-with-subagents.md` 1. Examples: `writing-plans/SKILL.md:163` — *"**REQUIRED SUB-SKILL:** Use superpowers:subagent-driven-development"*; `systematic-debugging/SKILL.md:177` — *"Use the `superpowers:test-driven-development` skill"*. Copied into `software-development`'s root unmodified, every one points at a namespace that is absent or routes back to the upstream copy. Step 2 therefore collapses into step 3 for every skill carrying one.

The breakage class is permanent, not one-off: 20 commits since 2026-01-01 added or moved lines containing `superpowers:` under `skills/`, and `writing-skills/SKILL.md:283` prescribes the qualified form as house style. Such changes auto-merge without conflict, so each future one would land silently broken.

### Why the fork wins

Qualified names are `pluginName:skillName`, independent of marketplace — corroborated live in this session's own skill listing, where `superpowers-developing-for-claude-code:developing-claude-code-plugins` is namespaced by plugin name while its marketplace is `superpowers-developing-for-claude-code-dev`. Keeping `"name": "superpowers"` in the fork preserves all 26 cross-references untouched.

Measured, by building the fork at pin `44c9b2d6` and merging upstream HEAD `b36e0829` (v6.3.0, five weeks, 415 lines across 13 skill files):

- The patch is **10 files changed, 117 insertions, 1933 deletions** — delete `skills/brainstorming/`, edit two lines of `using-superpowers/SKILL.md`, replace the `AGENTS.md` symlink with a regular file.
- The merge produced **exactly two conflicts**, both `DU` on the deleted directory, resolvable by `git rm -r` and fully scriptable.
- `skills/using-superpowers/SKILL.md`, the one file the fork edits, **auto-merged cleanly** even though upstream touched it.

Licence permits it: `LICENSE` is MIT, Copyright (c) 2025 Jesse Vincent; the only obligation is retaining the notice. Asking upstream to drop `brainstorming` is a non-starter — it is the plugin's first manifest keyword and its `defaultPrompt` is *"I've got an idea for something I'd like to build."*

### A fourth arrangement, evaluated and rejected

Claude Code marketplace entries can declare a plugin's components. The binary carries *"has conflicting manifests: both plugin.json and marketplace entry specify components. Set `strict: true` in marketplace entry or remove component specs from one location."* Since upstream's `.claude-plugin/plugin.json` declares no components, an entry-level `skills` array selecting 13 of 14 would conflict with nothing — curation with no fork and no vendoring.

**It dies on Codex.** `~/.codex/plugins/cache/superpowers-dev/superpowers/6.2.0/.codex-plugin/plugin.json` declares `"skills": "./skills/"` — a single path string, not an array. No subset is expressible. A Claude-only mechanism fails the destination's cross-harness requirement.

### Three defects the fork fixes as a side effect

1. **A non-reproducible marketplace.** `~/.codex/config.toml` currently declares `[marketplaces.superpowers-dev]` with `source_type = "local"` and `source = "/home/eranr/.claude/plugins/marketplaces/superpowers-dev"`. Codex's superpowers install is parasitic on a Claude install having happened first, in a specific order — it cannot reproduce on a fresh machine. Every other Codex marketplace on this machine is `source_type = "git"` with a real URL. Publishing the fork at a git URL converts the one non-reproducible marketplace into a reproducible one, which is a direct hit on the destination's fresh-machine requirement.
2. **The Codex hook never fires.** The Codex-side manifest declares `"hooks": {}` — an empty object — so superpowers' SessionStart hook does not register on Codex at all, even though `hooks/` is copied there. The mechanism exists (Codex supports `session_start` and sets `CLAUDE_PLUGIN_ROOT`); superpowers simply does not wire it.
3. **The missing Codex `AGENTS.md`**, still unfixed from the 2026-08-28 sweep. `git ls-files -s AGENTS.md` in the Codex cache returns mode `120000` (a symlink, tracked at the pin) while `git status --porcelain` reports ` D AGENTS.md` and no such file exists on disk. Codex's checkout drops the symlink, so 8,873 bytes of plugin-level guidance are silently absent. A fork fixes it at source by committing `AGENTS.md` as a regular file.

### Amendments the adversarial pass forced

Three, all accepted:

1. **The proposed drift check is insufficient.** Upstream's `using-superpowers/references/hermes-tools.md:31` contains `skill_view("brainstorming")` — **unqualified** — which auto-merges silently and is invisible to a `grep superpowers:brainstorming`. #63's check must cover unqualified forms.
2. **The patch is under-scoped.** `tests/brainstorm-server/` holds 12 live test files hard-coding `skills/brainstorming/scripts/...`, all orphaned by the deletion.
3. **A framing correction.** An earlier claim in this session's discussion held that ladder steps 2 and 3 use the same mechanism, so the ladder's real cliff sits between 1 and 2. On Claude Code that is overstated — the containment check is lexical and marketplace-entry declaration exists. The cliff holds only because Codex cannot express curation.

### Residual risks

- **Sequencing.** The fork's edited bootstrap points at `software-development:writing-specs`. Until that ships, every session injects a route to a skill that does not exist. `writing-specs` must land before or with the fork cutover. Owned by [#62](https://github.com/eranroseman/knowledge-harness/issues/62).
- **Name collision at cutover.** The fork keeps `"name": "superpowers"` — which is what preserves the 26 references — so it collides with the installed plugin; the binary carries a precedence message confirming the loser is shadowed. The cutover must uninstall first on both harnesses. Note `installed_plugins.json` also carries a **project-scope entry for `/home/eranr/memoria-vault` at a different sha** (`3dcbd5c4…`) pointing at the same install path — easy to miss, and it must be migrated too.
- **Fork staleness.** A fork nobody merges becomes a stale private snapshot — the exact failure `harness-backup` exists to avoid, reintroduced elsewhere. #63's monitor must watch upstream HEAD against the fork's merge-base, not just the fork against the installed cache. Without that the fork is strictly worse than step 1.

## Disposition table

Plugin-level disposition is the operative call. **Where a plugin is ladder step 1, all its components come across and per-skill rows are informational only.**

### Plugins

| Plugin | Harness | Step | Bucket | Fork call |
|---|---|---|---|---|
| `superpowers` | both | **3 — fork** | required | **fork** |
| `superpowers-developing-for-claude-code` | Claude | 3 — adapt | required | fork |
| `obsidian` | both | 1 — as-is | recommended | depend upstream |
| `writing-clearly-and-concisely` | both | 1 — as-is | recommended | depend upstream |
| `diataxis-skills` | both | 1 — as-is | recommended | depend upstream |
| `codex` (openai-codex bridge) | Claude | 1 — as-is | recommended | depend upstream |
| `codex-security` | Codex | 1 — as-is | recommended | depend upstream |
| `security-guidance` | Claude | 1 — as-is | recommended | depend upstream |
| `ponytail` | both | 1 — as-is | recommended | depend upstream |
| `caveman` | both | 1 — as-is | **disputed** | depend upstream |

`caveman`'s bucket is the one unresolved disagreement between passes — recommended on one reading, unrelated on another. Its core mode is general compressed communication, which a researcher benefits from identically; two of its skills (`caveman-commit`, `caveman-review`) are git-specific. Author's call.

On `writing-clearly-and-concisely` the fork question is a genuine three-way rather than two: obra already forked this skill from `softaworks/agent-toolkit` into `obra/superpowers-marketplace`, a marketplace already consumed here. Depending on that existing fork costs nothing and is a live option alongside depending on softaworks directly.

`security-guidance` ships **no skills, agents or commands at all** — it is hooks and nothing else: six hook registrations invoking a shared entrypoint over roughly 330KB of interdependent Python across 9 modules, plus an Agent SDK bootstrap at SessionStart with a 180-second timeout. Its Stop-hook half has no Codex equivalent; Codex's hook event set is `pre_tool_use`, `post_tool_use`, `permission_request`, `pre_compact`, `post_compact`, `session_start`, `session_end`, `user_prompt_submit`, `subagent_start`, `subagent_stop` — no main-agent Stop. Keeping it at step 1 avoids vendoring that Python for a Claude-only capability that `codex-security` already covers by another mechanism on the other harness.

### mattpocock's 18 installed skills

Installed standalone via `~/.agents/.skill-lock.json`, not as a plugin. Six were independently hash-matched against exact upstream commits and are pristine but stale: `domain-modeling` @ `54bc6b6`, `triage` @ `6a34259e`, `writing-for-agents` @ `4aaccb58`, `setup-matt-pocock-skills` @ `c66bdee`, `grilling` @ `86cba45f`, `wayfinder` @ `6a34259e`.

**To `shared-skills`:** `grilling`, `research`, `handoff`, `teach`, `to-questionnaire`, `wait-what`, `wayfinder`, `wizard`, `writing-for-agents`.

**To `software-development`:** `codebase-design`, `prototype`, `resolving-merge-conflicts`, `improve-codebase-architecture`, `triage`.

**Adapt (step 3):** `domain-modeling` — genuinely split on the sharing axis, and load-bearing for two adopted skills (`improve-codebase-architecture`, `wayfinder`) that reference it. `setup-matt-pocock-skills` — its disposition is not a sharing bucket at all; it is the transferable template for #62's setup mechanism, as [#85](https://github.com/eranroseman/knowledge-harness/issues/85) already found.

**Not adopted:** `grill-with-docs` and `to-tickets`, per #72's process-skill ruling.

This closes the four sharing verdicts #89 deferred to #75, plus `working-with-claude-code` and `superpowers` below — the six the ticket owed.

### mattpocock's 19 not-installed skills

The upstream roster is 37 skills; enumeration was certified by mechanical set-diff against `find skills -name SKILL.md`, empty in both directions. 18 installed, 19 not.

**All 19 are recommended not-adopted:** `ask-matt`, `code-review`, `diagnosing-bugs`, `implement`, `tdd`, `to-spec`, `grill-me`, `claude-handoff`, `implement-spec`, `loop-me`, `retro`, `setup-ts-deep-modules`, `writing-beats`, `writing-fragments`, `writing-shape`, `git-guardrails-claude-code`, `migrate-to-shoehorn`, `scaffold-exercises`, `setup-pre-commit`.

Adoption of something the author currently lives without required naming a concrete gap it fills; none did. The only dissent ran the other way — two verifiers argued `diagnosing-bugs`, `tdd` and the `writing-*` trio were declined without pricing an adaptation.

### The obra pair, and the double-install anomaly

`working-with-claude-code` and `developing-claude-code-plugins` are each installed **twice** — once inside the `superpowers-developing-for-claude-code` plugin, once standalone via the lockfile from the same upstream. Both are live simultaneously.

Both are **`software-development` only, step 3**. This corrects an earlier position taken in discussion, which argued `working-with-claude-code` should be shared because it documents the runtime both products run on. Both surveys placed it with the engineering side and that reading is accepted: it is a power-user runtime reference, and it does not separate from its sibling the way the shared reading required.

The dedupe itself is the author's call. What it costs to leave both live: two catalog entries with identical descriptions, each spending the per-entry skill-listing character budget; bare `/name` invocation stops resolving; and the plugin-side copy cannot be muted, since `skillOverrides` does not reach plugin skills.

### The four harness-backup skills

Recommendation only — other tickets own the final calls, and these are recorded so the recommendation routes rather than collides.

| Skill | Step | Home | Owning ticket |
|---|---|---|---|
| `finding-duplicate-functions` | 3 — adapt | `software-development` | #60 (the clearest vendoring case; also #64) |
| `consistency-audit` | 2 — as-is | `software-development` | #79 |
| `rethink` | 2 — as-is | `software-development` | #73 |
| `rethink-audit` | 2 — as-is | `software-development` | #73 |

The author ruled during this session that `rethink`/`rethink-audit` land in either `software-development` or `shared-skills`, and that **both** the public `eranroseman/rethink` repository and the `harness-backup` copies are deleted. Recorded on #73.

New finding for [#64](https://github.com/eranroseman/knowledge-harness/issues/64): **`finding-duplicate-functions` is absent from `harness-backup`'s README entirely**, so a fresh-machine restore silently omits it.

## The #60 input list

Every asset landing on ladder step 3, which #60 consumes directly.

| Asset | What must change |
|---|---|
| `brainstorming` → `writing-specs` | Rename; correct the description to name the funnel and the HARD-GATE; decide the Visual Companion's fate; decide the base version |
| `domain-modeling` | Sharing split resolution; adaptation scope to be set by #60 |
| `setup-matt-pocock-skills` | Adapt as the template for #62's setup mechanism |
| `working-with-claude-code` | Adaptation plus dedupe against the standalone install |
| `developing-claude-code-plugins` | Same |
| `finding-duplicate-functions` | Provenance header against `obra/superpowers-lab`; the local copy is a substantial rewrite (shell replaced with Python) |

**The list shrank because of the fork.** Earlier passes marked `systematic-debugging`, `test-driven-development`, `writing-plans`, `writing-skills` and `using-superpowers` as step-3 adaptations. Those marks were artifacts of the vendoring branch — the fork preserves the `superpowers:` namespace, so none of them needs adaptation. That collapse is the fork's clearest practical benefit.

**Two decisions #60 must make knowingly.**

The Visual Companion is separable but not free. It is 1,730 lines — `scripts/server.cjs` 723, `scripts/frame-template.html` 213, `scripts/start-server.sh` 209, `scripts/helper.js` 167, `scripts/stop-server.sh` 120, plus `visual-companion.md` 298 — and the whole `brainstorming` directory is 1,930 lines across 8 files. Nothing outside that directory references it, so dropping it costs one file deletion, one directory deletion, and about 19 lines removed from the skill body. But removing those 19 lines means "internals untouched" no longer describes the vendoring, which is what #72 specified. Note also that the companion loads a logo from an external site carrying the Superpowers version, opt-out via `SUPERPOWERS_DISABLE_TELEMETRY`.

The base version matters. Upstream HEAD replaced `brainstorming` with a three-path Spike/Bounded/Architectural router — 117 changed lines in `SKILL.md` — after the 6.2.0 text #72 judged. Vendoring from the pin ships a skill that is already a generation behind a substantial upstream improvement. Vendor from HEAD, freeze at the pin deliberately, or place `writing-specs` under #63's drift watch as a tracked adaptation.

## Anomalies

The five anomalies #75 carried, as resolved.

**Orphaned plugin caches — the original count was wrong.** `~/.claude/plugins/cache/` holds 16 directories; nine are the enabled pins. Of the other seven, three are superseded versions of still-enabled plugins (routine garbage-collection lag from a batch update on 2026-08-10), three are true orphans with no enabled successor (`interface-design`, `pr-review-toolkit`, `frontend-design` — the ticket named only the first), and one, `caveman/caveman/17f9f2ec2377`, is unreferenced **and unmarked**, with a larger roster than the pinned version. Ruled out of scope for map #53 as machine hygiene and filed as [#95](https://github.com/eranroseman/knowledge-harness/issues/95). The finding that matters for [#78](https://github.com/eranroseman/knowledge-harness/issues/78): the client's own `.orphaned_at` marker is **not** a complete signal, so a doctor check that trusts it misses exactly the case most warranting a look. Set subtraction against `installPath` is the reliable test.

**Double-installed obra skills** — covered above; cost of each branch supplied, decision open.

**Dormant `rethink` marketplace** — routed to #73 as one motion with the placement and deletion calls, per #51's deliberate bundling.

**Empty `claude-plugins-official` marketplace** — out of scope, filed with #95. Note it is a different registration from `claude-code-plugins`, which supplies the live `security-guidance` and must not be removed alongside it.

**Declared-asset policy gap** — the gap is real and was mislocated in #75's body. It lives in the global `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`, both of which cover only the `npx skills add -g` path with no declared-asset surface for native plugin installs. The author routed it to #64 rather than to #78 or to a patch of the two files, on the reasoning that a hand-maintained table is the weakest tier available under this repo's own *eliminate > mechanism > rule > prose* ordering and goes stale on the next install.

## A finding for #81

`to-spec` **is** mattpocock's PRD skill, renamed. `CHANGELOG.md:181` — *"`to-prd` is renamed to `to-spec`"*; `docs/engineering/to-spec.md:38` — *"Where did `/to-prd` go? It is this skill, renamed in v1.1."* So the premise that no vendor's roster contains a PRD skill is wrong in letter.

It is still worth more to [#81](https://github.com/eranroseman/knowledge-harness/issues/81) as a cited failure mode than as a donor, because upstream documents its own defect at `docs/engineering/to-spec.md:57`: *"The template leans hard on user stories, which is the wrong shape for architectural work: you end up writing stories nobody asked for around decisions that are really about interfaces and invariants."* That is a maintained vendor conceding in writing exactly the split #81 exists to draw. Its template divides cleanly along that line — product: Problem Statement, Solution, User Stories; engineering: Implementation Decisions, Testing Decisions; shared: Out of Scope, Further Notes.

Also minable for #81's agent-handoff dimension: `triage/AGENT-BRIEF.md`, 207 lines, MIT, already installed.

## Redistribution: lawful, and vendoring is the only structurally valid path

MIT permits modified copies; the binding condition is that `software-development` and `shared-skills` each ship the notice and copyright line.

Structurally, anything shipping **inside** the plugins must be a vendored copy in the plugin's own root. Agent Plugins §4.1 forbids symlink escape, and two independent Codex facts confirm it mechanically: Codex copies the plugin tree and **drops symlinks**, and `.codex-plugin/plugin.json` accepts `skills` as a single path string with arrays rejected, so no subset can be curated from one path.

This does not move step 2 to step 3. It changes what step 2 *means* — not "depend on upstream" but "vendor a byte-identical copy with provenance". The ladder distinguishes whether the text changed, not how it got there. The consequence worth recording: **every vendored copy, modified or not, becomes a #63 drift surface.** A dependency on a separately-distributed plugin — which is what the superpowers fork is — does not, because it keeps its own plugin root.

## Answered since this document was first written

- **"No repository outside the three products" is not a constraint** — verbatim: *"we can have as many repos as we want."* This was the only premise that would have overturned the fork. It does not hold, so the fork stands on its own merits rather than on any implied scarcity of repositories.
- **`caveman`'s bucket is `unrelated`.** Under the necessity test nothing in `software-development` invokes it, and a public plugin recommending an output-style mode recommends taste rather than capability. It stays installed; the bucket only decides whether the README names it.
- **The obra double-install is deduped in favour of the plugin**, dropping the standalone lockfile entries. Both skills are step-3 adaptations regardless, so the lockfile copy is the one with no future — and since `skillOverrides` reaches lockfile skills but not plugin skills, keeping the muteable copy while dropping the unmuteable one would be backwards.

## Open for the author

Ranked by downstream work unblocked. These route to other tickets and block nothing here.

1. **Should the fork be public?** MIT permits either. Public is better for the destination: a fresh machine can clone without credentials, whereas the current Codex marketplace uses an SSH remote, which is a credential dependency at setup.
2. **Does `writing-specs` track upstream `brainstorming` or freeze?** See the #60 section.
3. **Marketplace naming for the fork.** The plugin name must stay `superpowers` to preserve the cross-references, but the marketplace name should differ from `superpowers-dev` to keep the registrations unambiguous.
