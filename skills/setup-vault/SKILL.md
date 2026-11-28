---
name: setup-vault
description: Use when a person asks to create, repair, or provision a research-vault vault
disable-model-invocation: true
---

# Set up a vault

Use this only when the person explicitly invokes it. Keep the person in control of destination, CI, and every companion installation.

## Scaffold

Ask together: the destination `PATH` and whether they want read-only CI. Ask separately: whether they want the scheduled write-capable RW workflow. Do not infer either consent from the other. Ask separately whether they want the seeded `.obsidian/` (`--with-obsidian`): the plugins the vault declares, vendored at their pins, with their settings. Declining it leaves new notes wherever Obsidian puts them, and Core settings unjudged by doctor. Scaffold copies it once and only into a vault that has none; if it prints `skipped .obsidian/: already present`, relay the line and its fix (close Obsidian, move `.obsidian/` aside, run scaffold again) — never merge files into an existing `.obsidian/` by hand. That line is not a created path. Run scaffold before the compile tool's adopt step: adopt writes `.obsidian/` files when they are missing, and a seed that arrives second is skipped whole.

Fail closed on an ambiguous vault. If the destination is not unambiguous — two candidate vaults in play, "my vault" with no path attached, a `PATH` that could name either an existing vault or a new one — stop and ask which. Never resolve it yourself: not from the working directory, not from the most recently mentioned path, not from the only vault you happen to have seen. Scaffolding into the wrong tree writes files nobody asked for, and repairing a vault the person did not mean is worse; one question costs less than either.

Construct one command, with only the flags the user consented to:

```sh
python3 -m research_vault scaffold --vault PATH [--with-ci] [--with-rw-ci] [--with-obsidian]
```

Do not create directories or files by hand, substitute custom CI, use `git add .`, or make an unrelated commit. Run it: scaffold prints every path it created; report that list verbatim, and never present a path it did not print as committed. Paths such as `AGENTS.md`, `inbox/review-queue.md`, `system/templates/`, `system/bases/`, `system/glossary.md`, and `.git/hooks/pre-commit` are the contract, not an inventory of everything scaffold can create; CI paths appear only for their separately consented flags, and repairing an existing vault may create fewer paths than a fresh one.

A vault scaffolded with `--with-ci` on or before 2026-09-23 installs `research-vault @ git+…` in its workflow; the label is create-once, so edit the two `pip install` lines to `research-vault-core @ git+https://github.com/eranroseman/research-vault.git` by hand.

After adding CI to an existing vault, run `python3 -m research_vault verify --surface publish --recheck-commits all --vault PATH` once before the first publication: publish re-checks the commit that brought CI and every commit after it, so nothing else replays the commits before it.

## Diagnose

Run doctor after scaffold. Either accepted base override position is valid:

```sh
python3 -m research_vault --base URL doctor --vault PATH
python3 -m research_vault doctor --base URL --vault PATH
```

Report every doctor probe, not only failures — every row doctor prints — plus the inbox count and oldest age. `inbox`'s summary reports `oldest_age_days` directly — whole days since that date, 0 for one filed today, `None` only when the queue is empty — so state that figure rather than estimating the age yourself. Do not replace this with a `doctor --url` command or environment variable.

`doctor` always requires `--vault`; it has no vault-less mode. To check Zotero/BBT reachability before a vault exists, or independent of one, run `python3 -m research_vault probe [--base URL]` instead — it is the vault-less reachability instrument and takes no `--vault` flag.

## Obsidian's trust prompt

Obsidian (measured on 1.13.7 and 1.15.1) shows **Do you trust the author of this vault?** on every open of a vault whose `.obsidian/plugins/` holds a loadable manifest, until the person clicks **Trust author and enable plugins**; that click enables exactly the ids in `community-plugins.json` and is the consent step (lanes 2–3 spec §4.7). Tell the person to expect it on the first open and that the choice is kept per vault registration, outside the vault, so a second machine prompts again. Never run `plugins:restrict on` or `eval app.plugins.setEnable(false)`: either silences the prompt for that vault permanently with the plugins off and no message.

After the person has clicked, check that every seeded plugin loaded; two failures look different and one command cannot see both:

- A plugin whose constructor throws stays enabled but never loads. Compare `obsidian eval "[...app.plugins.enabledPlugins]"` with `obsidian eval Object.keys(app.plugins.plugins)`: an id in the first and not the second failed.
- A plugin whose `onload` throws is still listed as loaded. The only sign is Obsidian's own notice **Failed to load plugin “<id>”**: ask the person whether one appeared, and to reload once and look again.

`obsidian dev:errors` is empty for both, so an empty `dev:errors` proves nothing about loading; `plugins:enabled` lists configured ids whether or not they loaded and proves nothing either. Relay a failed id with its notice; never edit the plugin's files to make it load. Novel word count fails in its constructor when the process locale is `C.UTF-8` (`LANG` on WSL and in containers; `RangeError: Invalid language tag: c`): that is a host fact, not the seed's; tell the person to start Obsidian with `LANG` unset or `C`. Then `python3 -m research_vault seal --vault PATH` after the compile tool's adopt step, so the tool's own files under `wiki/` enter the compiled-page record.

## Rename by hand

A vault scaffolded on or before 2026-09-18 keeps its evidence layer under one of the stale names: `literatures/`. Doctor's `tree` row reports it (`UNMATCHED tree — stray literatures/: rename to literature/ by hand, then run capture --all`) and creates nothing while the old root stands; no verb renames a machine surface. The person runs `git mv literatures literature` in the vault, commits, then `python3 -m research_vault capture --all --vault PATH` — the notes re-render under the new root and `system/bibliography.json` regenerates. A `[[<citation key>]]` link names the note by key, not by folder, so it resolves as before; a `/literature/<citation key>.md` path link resolves once the rename lands, and a link whose path spells `literatures/` is re-pointed by hand.

## Provision companions

For each candidate in `PROVISION_COMPANIONS`, use this order: **Detect** → **Report** → obtain **per-item consent** → **Install or guide** → **Verify**. Detection and reporting never authorize installation. Do not propose or install unrelated packages.

After per-item consent, the scriptable candidate may use `claude plugin install kepano/obsidian-skills`; tell the person it is restart-to-activate, then verify after restart. If consent is absent, give the install command as an optional next step and do not run it.

Zotero .xpi installs are human-only wizard steps. The add-ons the vault asks for are declared once, in the two tables `README.md` embeds from `research_vault/templates/zotero-addons.md`: every add-on with its id and need (required, recommended, optional, excluded) and every preference value an add-on must hold, spelled as `prefs.js` spells it. Walk the person through installing each *required* row in Zotero's Add-ons window and setting each declared value — DOI Manager's two values in `prefs.js` before the add-on is installed, Meta Refresh's `titleSimilarityThreshold` seeded in `prefs.js` because its preferences pane clamps a typed value; never download, never install, never click, and never close Zotero for the user. MarkDB-Connect's source folder is the vault's `literature/` folder, never the vault root: the declared file pattern matches every Markdown name, so a root folder makes every other note a parse error on each sync (doctor checks only that the folder is set, #305). Confirm Reading Time loads — not `appDisabled`, no error in the Add-ons window — before relying on it. Doctor's `plugins` probe reads the same tables and fails until the declared values hold; its `advisory` probe warns on an `appDisabled` recommended add-on or an active excluded one.

Doctor can only read those facts when `.research-vault/machine.json` names the Zotero profile directory under `zotero_profile` (on this class of machine: `/mnt/c/Users/<user>/AppData/Roaming/Zotero/Zotero/Profiles/<id>.default`). Ask the person for it once; without it doctor reports the `fulltext-sync` probe, and the `bbt-git` and `plugins` probes, as SKIPPED, never as passed.

The compile tool is a Claude Code plugin and installs from its own marketplace, after per-item consent, with two commands the person runs (restart-to-activate):

```sh
claude plugin marketplace add AgriciDaniel/claude-obsidian
claude plugin install claude-obsidian@agricidaniel-claude-obsidian
```

Doctor's `compile-tool` probe reports the installed commit against the pin `32ac5a0`. A different commit holds publish: the row is in publish's closing set until the pin is restored or the person acknowledges the finding; doctor's own exit stays non-fatal. `$ROOT` is the plugin's `installPath` recorded in `~/.claude/plugins/installed_plugins.json` (the record doctor's `compile-tool` probe reads); `.research-vault/machine.json` may name a `claude_obsidian_root` that overrides it. Then adopt the vault into the tool once, with its own inspect-then-apply gate: `python3 "$ROOT/scripts/claude-obsidian.py" adopt PATH` (dry run, JSON on stdout), then `python3 "$ROOT/scripts/claude-obsidian.py" adopt PATH --apply --approved-plan-sha256 <approved_plan_sha256> --operation-id <operation.operation_id> --generated-at <generated_at>`, the three values read from the dry run's JSON — the approval hash covers `generated_at` and `operation_id`, which the apply run would otherwise regenerate from the clock and answer `PLAN_CHANGED`. The tool leaves the vault's existing `.gitignore` untouched (silently, not by refusing — measured 2026-09-14); append its rules by hand: `.vault-meta/`, `.mcp.json`, `.trash/`. Then `python3 -m research_vault seal --vault PATH`, so the tool's own files under `wiki/` enter the compiled-page record.

Once adopted, run the tool's wiki-lint skill over the vault once; its report is the tool's own health check, distinct from `doctor`.

The vault runs the tool in `generic` mode (`CONTEXT.md`'s paths); `python3 "$ROOT/scripts/claude-obsidian.py" mode get PATH` reads it back. Doctor's `compile-tool` row reports it beside the tool's pin; a mode other than generic holds publish the same way, until the mode is back to generic or the finding is acknowledged.
