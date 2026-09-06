# Plugin packaging mechanics — evidence for #11 (skill invocation policies) and #12 (plugin architecture & coexistence)

Disposition: historical (2026-09-06)

Research note, 2026-08-16. Observations made against **Claude Code 2.1.220** on this machine;
official docs quoted from code.claude.com are themselves littered with `v2.1.x` conditionals, so
anything marked *observed here* should be re-checked after CLI updates.

Primary evidence: the local plugin cache (`/home/eranr/.claude/plugins/`), local settings
(`/home/eranr/.claude/settings.json`), the live skill catalog of this session, and the official
docs (`https://code.claude.com/docs/en/plugins`, `/plugins-reference`, `/skills`,
`/plugin-marketplaces`, `/discover-plugins`, `/hooks`, `/settings`).

______________________________________________________________________

## 1. Plugin anatomy 2026

### 1.1 What "installed" looks like on disk

`~/.claude/plugins/` (all paths verified locally):

| Path                                                     | Role                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cache/<marketplace>/<plugin>/<version>/`                | The installed plugin payload. Version dir is the `plugin.json` version (`superpowers/6.2.0`, `ponytail/4.9.0`, `codex/1.0.6`, `obsidian/1.0.1`) or, when no version is declared, the git commit SHA (`caveman/309834233183`, `writing-clearly-and-concisely/3027f20f3181`). Matches the documented version-resolution order: plugin.json version → marketplace entry version → git SHA → archive digest → `unknown` (plugins-reference). |
| `marketplaces/<name>/`                                   | Full clone of each marketplace repo (catalog source).                                                                                                                                                                                                                                                                                                                                                                                    |
| `data/<plugin>-<marketplace>/`                           | Persistent per-plugin data dirs (`${CLAUDE_PLUGIN_DATA}`), survive updates. All empty here.                                                                                                                                                                                                                                                                                                                                              |
| `installed_plugins.json`                                 | `"version": 2` registry: per plugin ID (`name@marketplace`) an array of installs, each with `scope` (`user`/`project`), optional `projectPath`, `installPath`, `version`, `installedAt`, `lastUpdated`, `gitCommitSha`. Live example: `superpowers@superpowers-dev` has a `user` entry **and** a `project` entry with `projectPath: /home/eranr/memoria-vault`.                                                                          |
| `known_marketplaces.json`                                | marketplace name → `{source: {source: "github", repo}, installLocation, lastUpdated}`.                                                                                                                                                                                                                                                                                                                                                   |
| `.in_use` (inside each version dir), `.last_inuse_sweep` | Usage tracking (feeds the `/plugin` "Not used recently" list documented in discover-plugins).                                                                                                                                                                                                                                                                                                                                            |

Enablement lives in settings, not in the registry: `~/.claude/settings.json` here has
`"enabledPlugins": {"superpowers@superpowers-dev": true, ...}` plus `extraKnownMarketplaces`
mirroring the marketplace sources.

*Observed discrepancy:* `installed_plugins.json` records project-scope installs for
`/home/eranr/memoria-vault`, but that repo's `.claude/settings.json` contains **no**
`enabledPlugins` key (docs say project-scope installs are added to the project's
`.claude/settings.json`). Recorded as-is; not investigated further.

### 1.2 Plugin directory layout (shipped payload)

Docs (plugins-reference) + all five local plugins agree:

```text
plugin-root/
├── .claude-plugin/
│   ├── plugin.json          # manifest — the ONLY thing that goes in .claude-plugin/
│   └── marketplace.json     # only when the plugin repo is also its own marketplace
├── skills/<name>/SKILL.md   # + optional supporting files (references/, scripts/, README.md)
├── commands/<name>.md       # flat skill files (legacy; caveman also ships .toml variants)
├── agents/<name>.md         # subagent definitions
├── hooks/hooks.json         # hook config (default path)
├── .mcp.json / .lsp.json    # MCP / LSP servers
├── bin/                     # executables added to Bash PATH while enabled
├── monitors/monitors.json   # background monitors (experimental)
├── output-styles/, themes/  # output styles, themes (experimental)
├── settings.json            # plugin-shipped defaults; only `agent` and `subagentStatusLine` keys honored
└── scripts/, docs/, ...     # free-form; referenced via ${CLAUDE_PLUGIN_ROOT}
```

Component dirs must sit at plugin root, never inside `.claude-plugin/` (docs call this out as the
most common mistake). A single-skill plugin may put `SKILL.md` directly at plugin root.

### 1.3 plugin.json fields

Locally observed manifests are minimal — e.g.
`cache/superpowers-dev/superpowers/6.2.0/.claude-plugin/plugin.json` has only
`name`, `description`, `version`, `author`, `homepage`, `repository`, `license`, `keywords`.
Two hook-declaration styles observed:

- **Inline hooks object** — caveman's `plugin.json` embeds the full `hooks: {SessionStart: [...], UserPromptSubmit: [...]}` config.
- **Path string** — ponytail's `plugin.json` has `"hooks": "./hooks/claude-codex-hooks.json"` (it ships several harness-specific hook files and points Claude at one).
- **Default path** — superpowers/codex declare nothing; `hooks/hooks.json` is picked up automatically.

Full documented schema (plugins-reference): `name` (required, kebab-case, is the namespace),
`displayName`, `version`, `description`, `author{name,email,url}`, `homepage`, `repository`,
`license`, `keywords`, `metadata` (free-form), **`defaultEnabled`** (bool, default true),
component path overrides (`skills` — *adds to* default scan; `commands`/`agents`/`workflows`/
`outputStyles` — *replace* defaults; `hooks`/`mcpServers`/`lspServers` — path(s) or inline JSON),
`userConfig` (values prompted at enable time, stored under `pluginConfigs` in user settings only),
`dependencies` (other plugins, optional semver). Paths must be relative, starting `./`.
Substitution vars: `${CLAUDE_PLUGIN_ROOT}` (install dir), `${CLAUDE_PLUGIN_DATA}`
(persistent dir), `${CLAUDE_PROJECT_DIR}`.

Node deps are auto-installed at copy time (`npm ci --ignore-scripts` / bun equivalent, 60 s
timeout, lifecycle scripts disabled).

### 1.4 marketplace.json

Location: `.claude-plugin/marketplace.json` at the marketplace repo root. When a repo is a
single-plugin marketplace (superpowers, caveman, ponytail, obsidian-skills), it sits next to
`plugin.json` with `"source": "./"`. openai-codex is a multi-plugin repo: repo-root
`.claude-plugin/marketplace.json` points at `"source": "./plugins/codex"`.

Schema (plugin-marketplaces docs + local files): required `name` (kebab-case; the
`@marketplace` suffix users type), `owner{name, email?, url?}`, `plugins[]`. Optional top-level:
`metadata`, `renames` (v2.1.193+). Each plugin entry: required `name` + `source`; optional —
any plugin.json field plus `category`, `tags`, `strict` (default true: plugin.json is the
authority for components), `relevance`, `displayName`. Source types: relative path, `github`
(`repo`, `ref`/`sha` pins), `url` (git URL), `git-subdir` (`url`+`path`), `npm` (`package`),
`archive` (HTTPS zip + optional `sha256`; v2.1.224+), `command` (prints plugin dir; blockable by
admins). Caveman/ponytail reference `"$schema": "https://anthropic.com/claude-code/marketplace.schema.json"`.

Users attach marketplaces via `/plugin marketplace add <owner/repo|url|path>` or
`extraKnownMarketplaces` in settings; a repo's `.claude/settings.json` `extraKnownMarketplaces`
auto-registers for teammates once they trust the folder. A `settings` source type allows fully
inline marketplaces (no hosted repo) — plugins must then come from external sources and still be
enabled via `enabledPlugins` separately. Since v2.1.195, project-declared external plugins do
**not** auto-install for teammates; each user runs the shown `claude plugin install` once.

______________________________________________________________________

## 2. Skill catalog mechanics

### 2.1 How plugin skills reach the model

- Every enabled plugin's `skills/<dir>/SKILL.md` and `commands/*.md` become catalog
  entries **namespaced `plugin-name:skill-name`** (the plugin.json `name` is the prefix; a
  skill's frontmatter `name` replaces only the last segment, v2.1.216+).
- What the model sees per skill: name + `description` (+ `when_to_use`), truncated at **1,536
  characters** combined (skills doc, frontmatter table). Full SKILL.md body loads only on
  invocation. This session's own skill listing confirms: all superpowers/caveman/ponytail/
  obsidian/codex skills appear as `plugin:name — description text`.
- Namespacing means plugin skills *cannot* name-collide with personal/project skills — a plugin
  `deploy` and a project `deploy` coexist (skills doc: "Plugin skills use a plugin-name:skill-name
  namespace, so they can't conflict with other levels"). The bare `/name` also works while unambiguous.
- Non-plugin levels resolve name conflicts by source: enterprise > personal > project; any of
  those beat bundled skills; skill beats same-named `.claude/commands/` file.

### 2.2 Invocation-control frontmatter (works identically in plugin skills)

Docs (skills page, "Control who invokes a skill") — Claude Code accepts every frontmatter field
in plugin skills ("Claude Code skills at any level, including plugin skills: every field"):

| Frontmatter                      | User can invoke           | Model can invoke | Catalog presence                      |
| -------------------------------- | ------------------------- | ---------------- | ------------------------------------- |
| (default)                        | yes                       | yes              | name + description always in context  |
| `disable-model-invocation: true` | yes                       | **no**           | **description not in context at all** |
| `user-invocable: false`          | no (hidden from `/` menu) | yes              | description always in context         |

Live evidence from this very session's catalog:

- `/codex:review` and `/codex:adversarial-review` (`disable-model-invocation: true` in
  `cache/openai-codex/codex/1.0.6/commands/review.md`) are **absent** from the model-visible
  skill list — user-typed only, exactly as documented.
- `codex:codex-cli-runtime` (`user-invocable: false` in its SKILL.md) **is** listed with its
  description — model-invocable background knowledge.
- If the model calls a `disable-model-invocation` skill anyway, Claude Code blocks the call and
  instructs it not to reproduce the steps (documented).

Other catalog-relevant frontmatter: `when_to_use`, `argument-hint`, `arguments`,
`allowed-tools` / `disallowed-tools` (turn-scoped grants/blocks), `model`, `effort`,
`context: fork` + `agent` + `background` (run as subagent), `hooks` (skill-registered hooks),
**`paths`** (glob patterns limiting when the skill auto-activates — see §4), `shell`, `metadata`,
`license`, `compatibility`.

### 2.3 commands/ vs skills/ inside one plugin

Commands are "merged into skills" (docs) — a flat `commands/foo.md` and `skills/foo/SKILL.md`
both produce `plugin:foo`. Caveman ships **both** for the same names (`commands/caveman-commit.md`

- `skills/caveman-commit/SKILL.md`). *Observed here (2.1.220):* the catalog entry for
  `caveman:caveman-commit` carries the **command file's** description ("Generate terse
  caveman-style commit message"), not the SKILL.md's richer trigger text. That inverts the
  documented project-level rule ("if a skill and a command share the same name, the skill takes
  precedence"); plugin-level order is not documented. Version-dependent — don't rely on either
  winning. Practical rule for our plugin: ship each name in exactly one place (`skills/`).
  Caveman and ponytail also ship `commands/*.toml` variants — likely for other harnesses (both
  repos carry `gemini-extension.json`); whether Claude Code loads .toml commands is unverified
  (every observed .toml has a same-named .md or SKILL.md with identical description text, and the
  docs mention only .md command files).

### 2.4 skillOverrides — the big negative

`~/.claude/settings.json` here: `"skillOverrides": {"grilling": "name-only"}` — and it works
(this session's catalog shows `grilling` with **no description**, name only). But grilling is a
**personal** skill: `~/.claude/skills/grilling → ../../.agents/skills/grilling` (symlink verified).

The docs are explicit, twice:

> "Plugin skills are not affected by `skillOverrides`. Manage those through `/plugin` instead."
> (skills page, "Override skill visibility from settings")
> "Does not apply to plugin skills, which are managed through `/plugin`." (settings page, `skillOverrides` row)

And `/plugin` manages **whole plugins only** — enable/disable/uninstall per plugin; the detail
view lists components but offers no per-component toggle (discover-plugins, "Manage installed
plugins"). Consequences:

- We cannot collapse `superpowers:brainstorming` to name-only via settings the way grilling was tamed.
- Users of *our* plugin cannot collapse our process skill via `skillOverrides` either. If we want
  users to have a grilling-style dial, we must build it ourselves (e.g. userConfig option gating
  hook-injected context, or shipping the spine as a personal skill instead of a plugin skill).

skillOverrides values, for non-plugin skills: `"on"`, `"name-only"` (name listed, no
description), `"user-invocable-only"` (hidden from model, typable), `"off"` (hidden everywhere;
v2.1.199+ also hidden from SDK/Remote-Control command lists).

Permission rules are a separate lever that *should* reach plugin skills: `Skill(name)` /
`Skill(name *)` allow/deny rules (skills page, "Restrict Claude's skill access"). Deny rules block
model invocation. *Inferred from syntax, untested:* `Skill(superpowers:brainstorming)` in a
project's deny list would block model invocation per-repo; whether the description still occupies
catalog space when denied is undocumented.

______________________________________________________________________

## 3. Hooks from plugins

### 3.1 Registration

Three declaration forms, all observed locally (§1.3): inline in plugin.json (caveman), path
string in plugin.json (ponytail → `hooks/claude-codex-hooks.json`), default `hooks/hooks.json`
(superpowers, codex). Config shape is identical to settings-file hooks:
`{"hooks": {"<Event>": [{"matcher"?: "...", "hooks": [{"type": "command", "command": "...", "timeout"?, "statusMessage"?, "async"?, "shell"?}]}]}}`. Plugin hook commands use
`${CLAUDE_PLUGIN_ROOT}` for portability.

Local inventory of hook events in research-vault:

| Plugin            | Events                                                                                    | Config file                                                                       |
| ----------------- | ----------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| superpowers 6.2.0 | SessionStart (matcher `startup\|clear\|compact`)                                          | `hooks/hooks.json` → `run-hook.cmd session-start` (bash/Windows polyglot wrapper) |
| caveman           | SessionStart, UserPromptSubmit                                                            | inline in `.claude-plugin/plugin.json`                                            |
| ponytail 4.9.0    | SessionStart (matcher `startup\|resume\|clear\|compact`), SubagentStart, UserPromptSubmit | `hooks/claude-codex-hooks.json`                                                   |
| codex 1.0.6       | SessionStart, SessionEnd, Stop (timeout 900)                                              | `hooks/hooks.json`                                                                |

### 3.2 Merging, ordering, isolation (hooks docs)

- "When a plugin is enabled, its hooks merge with your user and project hooks" — merge, never replace.
- "**All matching hooks run in parallel.** If you define the same handler in more than one
  settings file, it runs once. A plugin's or skill's copy of the same handler stays separate."
  → dedup applies across settings files only; two plugins with identical commands both run.
- **Ordering across plugins on the same event is undocumented and effectively undefined**
  (parallel execution). Negative knowledge for us: you cannot arrange to inject context "after
  superpowers" deterministically.
- Failure isolation: a timed-out `command` hook is canceled, its output discarded, renders no
  decision, and doesn't block the tool call/other hooks. Invalid JSON/schema output → non-blocking
  error notice in transcript, action proceeds. Timeout defaults: 600 s for `command` (30 s on
  UserPromptSubmit); per-hook `timeout` overrides (caveman/ponytail set 5 s).
- SessionStart/UserPromptSubmit stdout (or `hookSpecificOutput.additionalContext`) becomes context
  Claude sees; each hook's output string capped at 10,000 chars. Multiple hooks' contexts
  accumulate — live proof: superpowers, caveman, ponytail and codex all inject at SessionStart in
  this harness and coexist.
- `disableAllHooks` / `allowManagedHooksOnly` (settings) can suppress plugin hooks wholesale;
  under `allowManagedHooksOnly` only managed-enabled plugins' hooks load.

### 3.3 What superpowers does with its hook (relevant to #12)

`hooks/session-start` reads `skills/using-superpowers/SKILL.md` **in full** and injects it
wrapped in `<EXTREMELY_IMPORTANT>You have superpowers...` as SessionStart additionalContext.
So the brainstorming-first mandate is not merely a catalog description — it is standing context
in every session (matcher: startup/clear/compact). Caveman and ponytail use the same lever for
their modes, with UserPromptSubmit trackers to maintain per-session mode state.

______________________________________________________________________

## 4. Scoping options: globally installed, conditionally active

Mechanisms that actually exist, strongest first:

1. **Per-scope enablement (`enabledPlugins`).** Scopes: user (`~/.claude/settings.json`),
   project (`.claude/settings.json`, team-shared), local (`.claude/settings.local.json`,
   gitignored), managed. Settings precedence: managed > CLI args > local > project > user.
   Documented explicitly: "Project settings take precedence over user settings, so setting a
   plugin to `false` in `~/.claude/settings.json` does not disable a plugin that the project's
   `.claude/settings.json` enables. To opt out of a project-enabled plugin on your machine, set
   it to `false` in `.claude/settings.local.json`." The converse — a project setting
   `"superpowers@superpowers-dev": false` disabling a user-enabled plugin in that repo — is
   *derived from the documented precedence order* (project > user), not stated verbatim;
   untested locally. `/plugin` install offers user/project/local scope interactively;
   `claude plugin install --scope project` scripts it.
2. **`defaultEnabled: false`** in plugin.json — installs disabled; user/repo opts in per scope.
3. **`paths` frontmatter on skills** — "Glob patterns that limit when this skill is activated...
   Claude loads the skill automatically only when working with files matching the patterns."
   File-glob, not repo-marker, but `*.md`-heavy vault work vs code work is exactly the split it
   can express. (Skills doc frontmatter table; version threshold not stated — verify on target CLI.)
4. **Hook-gated activation (vault marker).** A SessionStart hook can probe cwd (e.g. `.obsidian/`
   or a vault marker file) and emit activation context only on match, exiting 0 silently
   otherwise. No installed plugin does the conditional variant, but caveman/ponytail/superpowers
   prove the injection channel, and hook output is the only mechanism that can consult arbitrary
   repo state at session start.
5. **Per-repo rule files (caveman-init precedent).** `commands/caveman-init.md` +
   `src/tools/caveman-init.js` write an activation rule into repo-level agent files
   (`AGENTS.md`, `.cursor/rules/`, `.windsurf/rules/`, `.clinerules/`,
   `.github/copilot-instructions.md`, `.opencode/AGENTS.md`) — the repo opts in by carrying the
   text. Same pattern our plugin could use: a `/knowledge:init` that drops the vault-spine rule
   into the vault repo's AGENTS.md/CLAUDE.md.
6. **Description-conditioned triggering.** Softest: write trigger conditions into the skill
   description ("Use when working in an Obsidian vault / on .md notes..."). Precedent: the
   obsidian plugin's description ("Use when working with .md, .base, or .canvas files in an
   Obsidian vault") keeps five model-invocable skills quiet during dev work in research-vault.
7. **Permission rules per project** — `Skill(plugin:skill)` deny in a repo's
   `.claude/settings.json` (inferred, untested; see §2.4).
8. **Nested/project skills instead of plugin skills** — `.claude/skills/` in the vault repo, or
   nested dirs with directory-qualified names (`apps/web:deploy` pattern). Full skillOverrides
   support, no plugin namespace — but no marketplace distribution, which contradicts the
   "ship as plugin" decision unless used as a hybrid.

Also noted: repo-declared plugins (`enabledPlugins` in the repo's `.claude/settings.json`)
install at session start for cloud sessions, whereas user-scope plugins don't transfer (skills
doc §"Skills in Cowork and cloud sessions") — a point *for* project-scope activation if cloud
sessions matter.

______________________________________________________________________

## 5. Process-skill collision (superpowers brainstorming vs our spine)

**What actually decides which skill fires: the model's judgment over description text. There is
no precedence mechanism between semantically overlapping skills.** The docs' entire conflict
story (skills page, "Where skills live") is about *name* conflicts; plugin namespacing
deliberately makes same-named skills coexist. Two model-invocable skills whose descriptions both
claim "any creative work" simply compete in the model's head.

Superpowers stacks three reinforcements (all in
`cache/superpowers-dev/superpowers/6.2.0/skills/`):

1. `brainstorming/SKILL.md` description: "You MUST use this before any creative work — creating
   features, building components, adding functionality, or modifying behavior." — imperative
   wording in the catalog itself.
2. The SessionStart hook injects **all of** `using-superpowers/SKILL.md` every session (§3.3):
   "If you think there is even a 1% chance a skill might apply... you ABSOLUTELY MUST invoke the
   skill", plus a Skill Priority section: "When multiple skills apply, **process skills come
   first**... 'Let's build X' → superpowers:brainstorming first."
3. A red-flags table pre-rebutting every rationalization for skipping.

The documented escape hatch is inside using-superpowers itself:

> "User instructions (CLAUDE.md, AGENTS.md, GEMINI.md, etc, direct requests) take precedence
> over skills, which in turn override default behavior."

That is exactly the mechanism `/home/eranr/.claude/CLAUDE.md` already uses for grilling: a
routing rule in user instructions ("Invoke `grilling` only when the user directly asks...")
backed by `skillOverrides: name-only` to starve description matching. For a plugin-vs-plugin
collision only the first half of that recipe survives (§2.4: no skillOverrides on plugin skills).

**Mitigation inventory:**

| Mitigation                                                  | Works on plugin skills? | Notes                                                                                                                                                                                  |
| ----------------------------------------------------------- | ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CLAUDE.md / repo AGENTS.md routing rule                     | yes                     | The sanctioned lever; using-superpowers explicitly defers to it. Grilling precedent. Requires text in user/repo instructions, i.e. an init step or documented snippet.                 |
| Description wording (trigger-scoped, explicit non-triggers) | yes (ours)              | We control our spine's description; we cannot edit superpowers' (cache edits are overwritten on update — same failure mode the CLAUDE.md grilling note records for vendored SKILL.md). |
| `disable-model-invocation: true` on our spine               | yes                     | Removes collision entirely and removes auto-fire: user must type `/knowledge:...`. Codex-review precedent.                                                                             |
| `user-invocable: false`                                     | yes                     | Opposite dial; doesn't help with collision.                                                                                                                                            |
| `paths` frontmatter on our spine                            | yes                     | Auto-fire only around vault-file work.                                                                                                                                                 |
| `skillOverrides` name-only/off                              | **no**                  | Plugin skills exempt (double-sourced, §2.4).                                                                                                                                           |
| Per-repo `enabledPlugins: false` for superpowers            | yes (repo-level)        | Vault repo disables superpowers wholesale; blunt — loses debugging/TDD skills there too. Derived-from-precedence, untested.                                                            |
| Permission deny `Skill(superpowers:brainstorming)` per repo | probably                | Inferred from documented `Skill(name)` rule syntax; untested; catalog-space effect unknown.                                                                                            |
| Out-injecting via our own SessionStart mandate              | unreliable              | Hook ordering across plugins undefined (§3.2); two competing "MUST" injections with no arbitration. Dead end as a *primary* mechanism.                                                 |

______________________________________________________________________

## Anatomy reference (condensed)

**plugin.json** (`.claude-plugin/plugin.json`): `name`\* · `displayName` · `version` ·
`description` · `author{name,email,url}` · `homepage` · `repository` · `license` · `keywords[]` ·
`metadata{}` · `defaultEnabled` · `skills` (adds) · `commands`/`agents`/`workflows`/`outputStyles`
(replace) · `hooks` (path/array/inline) · `mcpServers` · `lspServers` ·
`experimental.{themes,monitors}` · `userConfig{}` · `dependencies[]` · `channels[]`.

**marketplace.json** (`.claude-plugin/marketplace.json`): `name`\* · `owner{name*,email,url}`\* ·
`plugins[]`\* (each: `name`\* · `source`\* \[rel-path | github | url | git-subdir | npm | archive |
command\] · any plugin.json field · `category` · `tags` · `strict` · `relevance`) · `metadata` ·
`renames`.

**Skill frontmatter** (all usable in plugin skills): `name` · `description` · `when_to_use` ·
`argument-hint` · `arguments` · `disable-model-invocation` · `user-invocable` · `allowed-tools` ·
`disallowed-tools` · `model` · `effort` · `context: fork` · `agent` · `background` · `hooks` ·
`paths` · `shell` · `metadata` · `license` · `compatibility`. Description+when_to_use capped at
1,536 chars in the catalog.

**Layout**: components at plugin root (`skills/`, `commands/`, `agents/`, `hooks/hooks.json`,
`.mcp.json`, `.lsp.json`, `bin/`, `monitors/`, `output-styles/`, `settings.json`); only
`plugin.json` inside `.claude-plugin/`. Cache: `~/.claude/plugins/cache/<mkt>/<plugin>/<version>/`.

## Coexistence-mechanisms table

| Mechanism                                               | What it controls                                                       | Evidence                                                                                                                                  |
| ------------------------------------------------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `enabledPlugins` per scope (user/project/local/managed) | whole plugin on/off per machine/repo                                   | `~/.claude/settings.json`; `installed_plugins.json` project entries; settings doc `enabledPlugins` note (opt-out via settings.local.json) |
| `defaultEnabled: false`                                 | ships disabled, explicit opt-in                                        | plugins-reference manifest schema                                                                                                         |
| Plugin namespace `plugin:skill`                         | name collisions across sources (not semantic ones)                     | skills doc "Where skills live"; live catalog                                                                                              |
| `disable-model-invocation`                              | removes skill from model catalog; user-typed only                      | codex `commands/review.md` + its absence from this session's catalog; skills doc table                                                    |
| `user-invocable: false`                                 | hides from `/` menu; model-only                                        | codex `skills/codex-cli-runtime/SKILL.md` + its presence in catalog                                                                       |
| `paths` frontmatter                                     | auto-activation only near matching files                               | skills doc frontmatter table (untested locally)                                                                                           |
| `skillOverrides`                                        | visibility of personal/project/bundled skills — **not plugin skills**  | settings.json `grilling: name-only` + bare catalog entry; skills doc L785; settings doc                                                   |
| Permission rules `Skill(name)` / `Skill(name *)`        | model's ability to invoke specific skills                              | skills doc "Restrict Claude's skill access" (plugin-namespaced form inferred, untested)                                                   |
| CLAUDE.md / AGENTS.md routing text                      | model's choice among competing skills                                  | `~/.claude/CLAUDE.md` grilling rule; using-superpowers "User Instructions" clause                                                         |
| SessionStart hook context injection                     | standing per-session mandates; can be made conditional on repo markers | superpowers `hooks/session-start`; caveman/ponytail hook configs                                                                          |
| Per-repo rule files dropped by an init command          | repo-opt-in activation for any harness                                 | caveman `commands/caveman-init.md`, `src/tools/caveman-init.js`                                                                           |
| Hook merge semantics                                    | plugins can't override or order each other's hooks                     | hooks doc: parallel, merge-not-replace, per-source copies                                                                                 |
| `/plugin` manager                                       | whole-plugin enable/disable/uninstall only                             | discover-plugins "Manage installed plugins"                                                                                               |

## Implications for #12 — real options (no decision here)

**A. Globally enabled plugin, description-scoped skills.** Spine skill description written like
obsidian's ("Use when working in the knowledge vault / on vault notes..."); optionally `paths`
frontmatter for `*.md` vault globs. Cheapest; coexists with the dev harness the way obsidian
already does. Trade-off: collision with brainstorming at ambiguous conversation openings is
decided by model judgment alone; superpowers' injected process-first mandate biases against us.

**B. Globally enabled plugin + routing text in user CLAUDE.md (grilling recipe, halved).**
Add a routing paragraph to `~/.claude/CLAUDE.md` ("knowledge-vault openings go through
`knowledge:<spine>`, not brainstorming") — the one lever using-superpowers explicitly honors.
Trade-off: the skillOverrides half of the grilling recipe is unavailable (plugin skills exempt),
so brainstorming's description stays in catalog at full strength; and the mitigation lives
outside the plugin (install-doc or init command must place it).

**C. Globally installed, repo-scoped activation.** `defaultEnabled: false` + enable in the vault
repo's `.claude/settings.json` (or settings.local.json); optionally the mirror move — disabling
superpowers in the vault repo (derived-from-precedence, verify empirically first). Cleanest
collision story; also the only variant whose plugins auto-carry into cloud sessions. Trade-off:
the knowledge spine won't fire in ad-hoc conversations outside vault repos, which may defeat a
"claims conversation openings" charter-analog; per-repo enablement is a setup step per vault.

**D. Conditional SessionStart hook inside a globally enabled plugin.** Hook probes for a vault
marker; injects the spine mandate only in vault repos, stays silent elsewhere; skills remain
catalog-visible everywhere (or pair with `paths`). Most precise; mirrors superpowers' own
strongest lever. Trade-off: injection ordering vs using-superpowers is undefined; in vault repos
where superpowers is also enabled you get dueling mandates unless combined with B or C.

**E. Hybrid: plugin for tools, personal/project skill for the spine.** Ship commands/agents/
hooks as the plugin; keep the collision-prone process spine as a personal or vault-repo skill so
`skillOverrides` and level-precedence apply to it. Trade-off: splits distribution (marketplace no
longer delivers the whole plugin); diverges from the "proper plugin" decision.

**Dead ends / negative knowledge:**

- `skillOverrides` on plugin skills — documented no-op, both directions of the collision.
- Per-component toggles in `/plugin` — don't exist; whole plugin only.
- Deterministically out-injecting or preceding another plugin's SessionStart context — hook
  ordering undefined, parallel execution.
- Editing superpowers' SKILL.md in the cache — silently overwritten on update (CLAUDE.md already
  records this failure mode for vendored skills; auto-update is on for these marketplaces).
- Shipping a plugin `settings.json` to influence global settings — only `agent` and
  `subagentStatusLine` keys are honored; a plugin cannot ship `skillOverrides`, hooks-into-settings,
  or permission rules that way.
- Relying on plugin-level command-vs-skill same-name precedence — observed behavior (2.1.220)
  contradicts the documented project-level rule; undocumented for plugins.
- `pluginConfigs` from project settings — ignored since v2.1.207 (user/managed only), so per-repo
  userConfig values can't scope behavior.
