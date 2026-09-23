---
name: setup-vault
description: Use when a person asks to create, repair, or provision a research-vault vault
disable-model-invocation: true
---

# Set up a vault

Use this only when the person explicitly invokes it. Keep the person in control of destination, CI, and every companion installation.

## Scaffold

Ask together: the destination `PATH` and whether they want read-only CI. Ask separately: whether they want the scheduled write-capable RW workflow. Do not infer either consent from the other.

Fail closed on an ambiguous vault. If the destination is not unambiguous — two candidate vaults in play, "my vault" with no path attached, a `PATH` that could name either an existing vault or a new one — stop and ask which. Never resolve it yourself: not from the working directory, not from the most recently mentioned path, not from the only vault you happen to have seen. Scaffolding into the wrong tree writes files nobody asked for, and repairing a vault the person did not mean is worse; one question costs less than either.

Construct one command, with only the flags the user consented to:

```sh
python3 -m research_vault scaffold --vault PATH [--with-ci] [--with-rw-ci]
```

Do not create directories or files by hand, substitute custom CI, use `git add .`, or make an unrelated commit. Run it: scaffold prints every path it created; report that list verbatim, and never present a path it did not print as committed. Paths such as `AGENTS.md`, `inbox/review-queue.md`, `system/templates/`, `system/bases/`, `system/glossary.md`, and `.git/hooks/pre-commit` are the contract, not an inventory of everything scaffold can create; CI paths appear only for their separately consented flags, and repairing an existing vault may create fewer paths than a fresh one.

A vault scaffolded with `--with-ci` before 2026-09-17 installs `research-vault @ git+…` in its workflow; the label is create-once, so edit the two `pip install` lines to `research-vault-core @ git+https://github.com/eranroseman/research-vault.git` by hand.

## Diagnose

Run doctor after scaffold. Either accepted base override position is valid:

```sh
python3 -m research_vault --base URL doctor --vault PATH
python3 -m research_vault doctor --base URL --vault PATH
```

Report every doctor probe, not only failures — thirteen rows — plus the inbox count and oldest age. `inbox`'s summary reports `oldest_age_days` directly — whole days since that date, 0 for one filed today, `None` only when the queue is empty — so state that figure rather than estimating the age yourself. Do not replace this with a `doctor --url` command or environment variable.

`doctor` always requires `--vault`; it has no vault-less mode. To check Zotero/BBT reachability before a vault exists, or independent of one, run `python3 -m research_vault probe [--base URL]` instead — it is the vault-less reachability instrument and takes no `--vault` flag.

## Rename by hand

A vault scaffolded before 2026-09-17 keeps its evidence layer under one of the stale names: `literatures/`. Doctor's `tree` row reports it (`UNMATCHED tree — stray literatures/: rename to literature/ by hand, then run capture --all`) and creates nothing while the old root stands; no verb renames a machine surface. The person runs `git mv literatures literature` in the vault, commits, then `python3 -m research_vault capture --all --vault PATH` — the notes re-render under the new root and `system/bibliography.json` regenerates. Every `[[<citation key>]]` link resolves as before; nothing else in the vault names the directory.

## Provision companions

For each candidate in `PROVISION_COMPANIONS`, use this order: **Detect** → **Report** → obtain **per-item consent** → **Install or guide** → **Verify**. Detection and reporting never authorize installation. Do not propose or install unrelated packages.

After per-item consent, the scriptable candidate may use `claude plugin install kepano/obsidian-skills`; tell the person it is restart-to-activate, then verify after restart. If consent is absent, give the install command as an optional next step and do not run it.

Zotero .xpi installs are human-only wizard steps. The add-ons the vault asks for are declared once, in the table `README.md` embeds from `research_vault/templates/zotero-addons.md` (required, recommended, optional, each with its add-on id and, where one exists, the preference that switches its automatic mode on). Walk the person through installing each *required* row in Zotero's Add-ons window and enabling the automatic-mode preferences; never download, never install, never click, and never close Zotero for the user. Doctor's `plugins` probe reads the same table and reports each add-on's `active`/`appDisabled` state and whether its automatic mode is on.

Doctor can only read those facts when `.research-vault/machine.json` names the Zotero profile directory under `zotero_profile` (on this class of machine: `/mnt/c/Users/<user>/AppData/Roaming/Zotero/Zotero/Profiles/<id>.default`). Ask the person for it once; without it doctor reports `fulltext-sync`, `bbt-git` and `plugins` as SKIPPED, never as passed.

The compile tool is a Claude Code plugin and installs from its own marketplace, after per-item consent, with two commands the person runs (restart-to-activate):

```sh
claude plugin marketplace add AgriciDaniel/claude-obsidian
claude plugin install claude-obsidian@agricidaniel-claude-obsidian
```

Doctor's `compile-tool` probe reports the installed commit against the pin `32ac5a0`; a different commit is a warning, not a failure. `$ROOT` is the plugin's `installPath` recorded in `~/.claude/plugins/installed_plugins.json` (the record doctor's `compile-tool` probe reads); `.research-vault/machine.json` may name a `claude_obsidian_root` that overrides it. Then adopt the vault into the tool once, with its own inspect-then-apply gate: `python3 "$ROOT/scripts/claude-obsidian.py" adopt PATH` (dry run, JSON on stdout), then `python3 "$ROOT/scripts/claude-obsidian.py" adopt PATH --apply --approved-plan-sha256 <approved_plan_sha256> --operation-id <operation.operation_id> --generated-at <generated_at>`, the three values read from the dry run's JSON — the approval hash covers `generated_at` and `operation_id`, which the apply run would otherwise regenerate from the clock and answer `PLAN_CHANGED`. The tool leaves the vault's existing `.gitignore` untouched (silently, not by refusing — measured 2026-09-14); append its rules by hand: `.vault-meta/`, `.mcp.json`, `.trash/`.

Once adopted, run the tool's wiki-lint skill over the vault once; its report is the tool's own health check, distinct from `doctor`.

The vault runs the tool in `generic` mode (`CONTEXT.md`'s paths); `python3 "$ROOT/scripts/claude-obsidian.py" mode get PATH` reads it back. No doctor row observes it yet (lane 3a).
