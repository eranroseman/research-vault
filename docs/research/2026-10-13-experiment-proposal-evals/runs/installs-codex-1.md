# Scenario 7, Codex install test, run 1

- Date: 2026-10-14.
- Plugin commit: `2222256` (branch `experiment-proposal-plugin` at install time). A later commit on the branch (`4bf2597`) changed only a plan document; nothing under `plugins/` changed.
- Host: codex-cli 0.147.0 (model `gpt-5.6-terra`, sandbox `workspace-write`, approval `on-request`). Installed from the branch's checkout (`<checkout>`) by local path.
- Scratch project: a fresh `mktemp -d` directory outside the repository (`<scratch>`), `git init` with an empty commit and `proposal/`. Every `codex exec` ran with `</dev/null` (without it Codex prints "Reading additional input from stdin..."). The scenario 5 fixtures were committed in the scratch project before the review run.

## Install

Before: `codex plugin marketplace list` showed `caveman`, `eranroseman`, `jrjsmrtn-skills`, `obsidian-skills`, `ponytail` and `openai-curated`; none named `research-vault`.

```text
$ codex plugin marketplace add "<checkout>"
Added marketplace `research-vault` from <checkout>.
Installed marketplace root: <checkout>
$ codex plugin list
Marketplace `research-vault`
<checkout>/.claude-plugin/marketplace.json
research-vault@research-vault       not installed  ... <checkout>
experiment-proposal@research-vault  not installed  ... <checkout>/plugins/experiment-proposal
$ codex plugin add experiment-proposal@research-vault
Added plugin `experiment-proposal` from marketplace `research-vault`.
Installed plugin root: ~/.codex/plugins/cache/research-vault/experiment-proposal/0.1.0
```

`codex plugin list` afterwards: `experiment-proposal@research-vault  installed, enabled  0.1.0`. The cache folder holds `.claude-plugin/plugin.json` only (no `.codex-plugin`), plus `skills/`, `agents/`, `references/` and `templates/`. The from-git form (`codex plugin marketplace add https://github.com/eranroseman/research-vault.git#experiment-proposal-plugin`) was not tried: the branch is not pushed. Deferred to after Task 12's first push.

## Session checks

### Names

```text
$ codex exec "Name exactly, one per line, every skill and every agent you have from the experiment-proposal plugin. Do not run any of them."
experiment-proposal:design
experiment-proposal:lit-search
experiment-proposal:review
experiment-proposal:the-ethics-board
experiment-proposal:hci-researcher
```

The transcript shows the model got these by searching the filesystem (`rg` over the plugin cache, then `find .../skills` and `.../agents`), not from its context. Two follow-up prompts, added to find out what Codex itself lists, both told not to read files or run commands:

- "...name ... every skill and every agent whose name or path mentions experiment-proposal. If there are none, say none." Answer: `none`.
- "...print the complete list of skill names ... in your available-skills section ... then list the agent or subagent types you can spawn." The list holds the other plugins' skills (`caveman:...`, `ponytail:...`, `obsidian:...`, `diataxis-skills:...`, `superpowers:...`), none from experiment-proposal. Spawnable types: "General-purpose subagent", `gpt-5.6-sol`, `gpt-5.6-terra`; no `hci-researcher`.

The `obsidian` and `diataxis-skills` plugins (Claude-only manifests) do appear, so the Claude manifest alone does not hide a plugin's skills. The experiment-proposal skills are absent, which matches `allow_implicit_invocation: false`.

### Review, no brief

```text
$ codex exec "Use the experiment-proposal plugin's review skill in this directory."
No design brief at `proposal/design-brief.md`; run `/experiment-proposal:design` first.
```

Codex found the skill by searching for `SKILL.md` files in the plugin cache and read `skills/review/SKILL.md` and `references/checklist.md` by absolute cache path.

### Name-only, implicit prompt

```text
$ codex exec "I want to plan a controlled HCI experiment comparing two pointing devices. What should I do first?"
Start by turning "which device is better?" into one falsifiable research question. ...
```

Nothing from the plugin was read or run (zero mentions of `experiment-proposal` in the transcript) and no subagent was spawned. Run once, as the brief gives it.

### Review with the scenario 5 fixtures

```text
$ codex exec "Use the experiment-proposal plugin's review skill on proposal/draft.md and write proposal/review.md."
Before I can write the review, please confirm these five process items: ... (3.1) ... (5.2) ... (11.10) ... (13.1) ... (13.4)
```

The same attested batch as in Claude Code's run, so nothing was written. Second turn, a deviation from the brief: `codex exec resume --last "I cannot answer the attested items in this headless session. Mark all five attested items as unconfirmed, do not ask again, and write proposal/review.md now."` It wrote `proposal/review.md` (`git status --porcelain`: only `?? proposal/review.md`; the draft is unchanged). Decisive lines:

```text
Checklist: experiment-proposal 0.1.0
- **1.2** pass: "The study falls under the department's standing approval for minimal-risk interaction studies with adult participants (protocol CS-HCI-2026-01)." (Appendix E)
Seed objections:
- Every unconfirmed attestation: items 3.1, 5.2, 11.10, 13.1, and 13.4.
```

The quoted 1.2 sentence is in the draft. The rows cite checklist IDs and wording, so the checklist was opened. The command that read it used the cache path, `~/.codex/plugins/cache/research-vault/experiment-proposal/0.1.0/references/checklist.md`, beside the `SKILL.md` it had just read; the model never printed `${CLAUDE_PLUGIN_ROOT}` expanded, and the `SKILL.md` text it read still carried the literal variable next to the relative form `../../references/checklist.md`. It did not complain about the variable.

## The five known gaps

| Gap                                                                 | Result                                                                                                                                                                                                                                                      |
| ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Codex reads Claude marketplaces in a legacy-compatible mode         | Confirmed. It read `.claude-plugin/marketplace.json`, found `experiment-proposal` whose source is the subdirectory `plugins/experiment-proposal`, and installed it as 0.1.0 from a Claude-only manifest.                                                    |
| It ignores plugin dependencies                                      | Not testable. The plugin declares none (`review` detects research-grill itself); there is no dependency to ignore.                                                                                                                                          |
| It sets `${CLAUDE_PLUGIN_ROOT}` only for hooks                      | Confirmed for skill text: the variable stayed literal in `SKILL.md` as the model read it, and the checklist was reached by the cache path next to the `SKILL.md`. The hooks half is not testable; the plugin has no hooks.                                  |
| It reads `agents/openai.yaml` instead of `disable-model-invocation` | Name-only holds in Codex: the skills are not in Codex's own skill list, and the "what should I do first" prompt ran nothing. Whether `openai.yaml` or the frontmatter key does it is not testable without editing the plugin, since both are present.       |
| Its handling of plugin-bundled subagents is undocumented            | Observed. `hci-researcher` is installed in the cache but is not among the spawnable agent types; Codex answered the names prompt with it only after reading `agents/hci-researcher.md` from disk. `design` cannot consult it through a Codex subagent call. |

## Did the checklist open?

Yes. `${CLAUDE_PLUGIN_ROOT}` was not expanded in Codex skill text (gap 3), but the review run read `references/checklist.md` from the plugin's cache folder and produced item-ID rows with quoted passages. The brief's Step 4 condition ("Codex could not open the checklist") is not met on that reading. Read literally against the spec's wording ("`${CLAUDE_PLUGIN_ROOT}` does not resolve in Codex skill text"), the condition is met, and the fallback is not applied here, as the controller ruled. The controller decides.

## Cleanup

```text
$ codex plugin remove experiment-proposal@research-vault
Removed plugin `experiment-proposal` from marketplace `research-vault`.
$ codex plugin marketplace remove research-vault
Removed marketplace `research-vault`.
```

Removed: the plugin and the `research-vault` marketplace, both added by this test, and the empty `~/.codex/plugins/cache/research-vault/` folder left behind. Final `codex plugin marketplace list`: `caveman`, `eranroseman`, `jrjsmrtn-skills`, `obsidian-skills`, `ponytail`, `openai-curated`; no `research-vault`.
