---
name: setup-vault
description: Use when a person asks to create, repair, or provision a knowledge-harness vault
disable-model-invocation: true
---

# Set up a vault

Use this only when the person explicitly invokes it. Keep the person in control of destination, CI, and every companion installation.

## Scaffold

Ask together: the destination `PATH` and whether they want read-only CI. Ask separately: whether they want the scheduled write-capable RW workflow. Do not infer either consent from the other.

Construct one command, with only the flags the user consented to:

```sh
python3 -m knowledge_harness scaffold --vault PATH [--with-ci] [--with-rw-ci]
```

Do not create directories or files by hand, substitute custom CI, use `git add .`, or make an unrelated commit. Run scaffold and report its exact printed created paths. On a fresh vault, scaffold can create `.git/hooks/pre-commit`, `.gitignore`, `.harness/machine.json`, `AGENTS.md`, `inbox/review-queue.md`, `index.md`, `literatures/.gitkeep`, `log.md`, `log/.gitkeep`, `projects/.gitkeep`, `synthesis/index.md`, `system/bases/open-questions.base`, `system/bases/trust-tier.base`, `system/glossary.md`, and `system/templates/` daily, literature, project, and synthesis templates; CI paths appear only for their separately consented flags. It may create fewer paths when repairing an existing vault. Say only scaffold-created paths are committed; never claim unrelated changes were committed.

## Diagnose

Run doctor after scaffold. Either accepted base override position is valid:

```sh
python3 -m knowledge_harness --base URL doctor --vault PATH
python3 -m knowledge_harness doctor --base URL --vault PATH
```

Report every doctor probe, not only failures, plus the inbox count and oldest age. Do not replace this with a `doctor --url` command or environment variable.

`doctor` always requires `--vault`; it has no vault-less mode. To check Zotero/BBT reachability before a vault exists, or independent of one, run `python3 -m knowledge_harness probe [--base URL]` instead — it is the vault-less reachability instrument and takes no `--vault` flag.

## Provision companions

For each candidate in `PROVISION_COMPANIONS`, use this order: **Detect** → **Report** → obtain **per-item consent** → **Install or guide** → **Verify**. Detection and reporting never authorize installation. Do not propose or install unrelated packages.

After per-item consent, the scriptable candidate may use `claude plugin install kepano/obsidian-skills`; tell the person it is restart-to-activate, then verify after restart. If consent is absent, give the install command as an optional next step and do not run it.

Zotero .xpi installs are human-only wizard steps: BBT required; MarkDB-Connect optional. Explain where the person performs the wizard and what to verify afterward, but never download, never install, never click, and never close Zotero for the user.

The whole-library bibliography auto-export is a human-only wizard step of the same class. Doctor reports it `UNMATCHED` with the target it expects, so give the person the exact target path doctor reported and have them add an auto-export in BBT Preferences with whole-library scope, the Better CSL JSON translator, and keep updated enabled. Then re-run doctor to verify. Never register an auto-export for them, and never say an auto-export exists until doctor reports `autoexport` MATCHED.
