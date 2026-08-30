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

## Diagnose

Run doctor after scaffold. Either accepted base override position is valid:

```sh
python3 -m research_vault --base URL doctor --vault PATH
python3 -m research_vault doctor --base URL --vault PATH
```

Report every doctor probe, not only failures, plus the inbox count and oldest age. `inbox`'s summary reports `oldest_age_days` directly — whole days since that date, 0 for one filed today, `None` only when the queue is empty — so state that figure rather than estimating the age yourself. Do not replace this with a `doctor --url` command or environment variable.

`doctor` always requires `--vault`; it has no vault-less mode. To check Zotero/BBT reachability before a vault exists, or independent of one, run `python3 -m research_vault probe [--base URL]` instead — it is the vault-less reachability instrument and takes no `--vault` flag.

## Provision companions

For each candidate in `PROVISION_COMPANIONS`, use this order: **Detect** → **Report** → obtain **per-item consent** → **Install or guide** → **Verify**. Detection and reporting never authorize installation. Do not propose or install unrelated packages.

After per-item consent, the scriptable candidate may use `claude plugin install kepano/obsidian-skills`; tell the person it is restart-to-activate, then verify after restart. If consent is absent, give the install command as an optional next step and do not run it.

Zotero .xpi installs are human-only wizard steps: BBT required; MarkDB-Connect optional. Explain where the person performs the wizard and what to verify afterward, but never download, never install, never click, and never close Zotero for the user.

The whole-library bibliography auto-export is a human-only wizard step of the same class. Doctor reports it `UNMATCHED` with the target it expects, so give the person the exact target path doctor reported and have them add an auto-export in BBT Preferences with whole-library scope, the Better CSL JSON translator, and keep updated enabled. Then re-run doctor to verify. Never register an auto-export for them, and never say an auto-export exists until doctor reports `autoexport` MATCHED.
