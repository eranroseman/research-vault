# Alteration inventory sweep

Resolves [#56](https://github.com/eranroseman/knowledge-harness/issues/56). Answers
"what do we alter" across the installed harness by instrument, not memory: every
enabled plugin diffed against its exact pinned commit **on both Claude Code and
Codex**, skills directories reconciled against the skill-lock installer, and
custom agents enumerated.

## Method

For each of the 9 enabled Claude Code plugins, `installed_plugins.json` records an
exact `gitCommitSha` pinned at install time. Each plugin's marketplace is a live
local git clone under `~/.claude/plugins/marketplaces/<marketplace>/`. Where that
clone's checked-out `HEAD` matched the recorded pin exactly, the plugin's cache
directory (`~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`) was diffed
directly against the corresponding subpath in the marketplace clone (the subpath
per plugin comes from the marketplace's own `.claude-plugin/marketplace.json`
`source` field). Two marketplaces (`caveman`, `claude-code-plugins`) had since been
git-pulled past the recorded pin; for those, the exact pinned commit was fetched
from its GitHub origin and extracted with `git archive` into a throwaway
directory, so the diff is against the true pin rather than a drifted local
checkout. `.in_use` (a Claude Code runtime lock marker) and Python bytecode caches
(`__pycache__`, `.mypy_cache`) were excluded as tooling noise, not content.

Skills installed via `npx skills add -g` are tracked in `~/.agents/.skill-lock.json`
and live at `~/.agents/skills/<name>`, symlinked into `~/.claude/skills/<name>` and
`~/.codex/skills/<name>` (the three-tier topology this harness uses). Reconciliation
here means: does every directory on disk have a lockfile entry, and vice versa.

Custom agents means the contents of `~/.claude/agents/`.

## Findings: plugin diff (9 enabled plugins)

| Plugin                                 | Marketplace                                | Pinned commit | Result                                                                                                                                                                                                                                                                                                                                                                                                      |
| -------------------------------------- | ------------------------------------------ | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| security-guidance                      | claude-code-plugins                        | `6a9c2db`     | Clean (verified against exact pin, fetched fresh — marketplace HEAD had drifted)                                                                                                                                                                                                                                                                                                                            |
| ponytail                               | ponytail                                   | `2ed6c52`     | Clean — no local divergence from the pin found                                                                                                                                                                                                                                                                                                                                                              |
| superpowers                            | superpowers-dev                            | `44c9b2d`     | **Modified**: cache's `README.md` carries a "We're Hiring!" section that the pinned commit's own `README.md` does not contain (confirmed via `git show <pin>:README.md`, zero matches). Content-only (not a skill/hook), and shaped like a stale leftover from an earlier install that an update didn't fully refresh, rather than a deliberate edit — but it is a real, confirmed difference from the pin. |
| caveman                                | caveman                                    | `3098342`     | Clean (verified against exact pin, fetched fresh — marketplace HEAD had drifted significantly, which produced a large false-positive diff before pinning down the real commit)                                                                                                                                                                                                                              |
| obsidian                               | obsidian-skills                            | `a1dc48e`     | Clean                                                                                                                                                                                                                                                                                                                                                                                                       |
| writing-clearly-and-concisely          | agent-toolkit                              | `3027f20`     | Clean                                                                                                                                                                                                                                                                                                                                                                                                       |
| diataxis-skills                        | jrjsmrtn-skills                            | `e1e15d8`     | Clean (this cache dir is itself a git checkout at the pin; `git status --porcelain` shows only the untracked `.in_use` marker)                                                                                                                                                                                                                                                                              |
| codex                                  | openai-codex                               | `db52e28`     | Clean                                                                                                                                                                                                                                                                                                                                                                                                       |
| superpowers-developing-for-claude-code | superpowers-developing-for-claude-code-dev | `74afe93`     | Clean                                                                                                                                                                                                                                                                                                                                                                                                       |

**8 of 9 plugins have zero local content divergence from their pin.** The one
exception (superpowers) is a leftover README paragraph, not a functional change.

**Note on "ponytail is the plugin we modified":** no local divergence from
ponytail's pin exists on either harness. This doesn't necessarily contradict that
recollection — if the modification was authored upstream (a fork or contribution
already folded into the pinned commit itself) rather than applied as a local
uncommitted edit, it would be invisible to this diff by construction, since both
sides already include it. Worth clarifying which sense was meant before #60 or
#75 treat ponytail as the vendoring precedent on the strength of a local-diff
check alone.

## Findings: plugin diff, Codex side

Codex maintains its own separate plugin cache under `~/.codex/plugins/cache/`,
enabled per `~/.codex/config.toml`. Most Codex-side cache directories are
themselves git checkouts (`git status --porcelain` inside each one reveals local
edits directly, no marketplace-subpath reconstruction needed); the few that
aren't were diffed against the same marketplace clones used above (`caveman` and
`superpowers-dev` marketplace sources are shared between the two harnesses;
`config.toml` records the Codex-side pin per marketplace, which for `caveman` and
`jrjsmrtn-skills` differs from the Claude-side pin — expected, since the two
harnesses' plugins were installed/updated at different times, not itself an
alteration). 7 plugins enabled for Codex map onto plugins already covered above,
plus one Codex-only plugin:

| Plugin                            | Result                                                                                                                                                                                                                                                                                                                                                                                  |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| ponytail                          | Clean                                                                                                                                                                                                                                                                                                                                                                                   |
| superpowers                       | **Modified**: `AGENTS.md` is present in the pinned commit but **absent** from the Codex-side cache (confirmed via `git show HEAD:AGENTS.md` in the marketplace clone — the file exists there). A different divergence from the Claude-side one (README addition vs. AGENTS.md deletion) — the two harnesses' copies of the same plugin have drifted from the pin in two unrelated ways. |
| caveman                           | Clean (only an untracked `.codex-marketplace-install.json` metadata file)                                                                                                                                                                                                                                                                                                               |
| obsidian                          | Clean (only an untracked `.codex-marketplace-install.json` metadata file)                                                                                                                                                                                                                                                                                                               |
| writing-clearly-and-concisely     | Clean (only an untracked `.codex-plugin` metadata dir)                                                                                                                                                                                                                                                                                                                                  |
| diataxis-skills                   | Clean                                                                                                                                                                                                                                                                                                                                                                                   |
| codex-security (`openai-curated`) | Not applicable — no `[marketplaces.openai-curated]` entry in `config.toml` and no external git source found; this plugin appears bundled with the Codex CLI itself rather than fetched from a separate pinned upstream, so "diff against pinned upstream" doesn't apply to it.                                                                                                          |

`security-guidance`, `openai-codex` (the Claude→Codex bridge itself), and
`superpowers-developing-for-claude-code` are Claude-Code-only and have no
Codex-side counterpart to check.

## Findings: skills reconciliation

`~/.agents/skills/` contains exactly the 20 entries locked in `.skill-lock.json`
— a perfect 1:1 match, no orphans, nothing missing. Named explicitly (a count
alone doesn't let a reader verify anything):

18 from `mattpocock/skills`: `codebase-design`, `domain-modeling`, `grilling`,
`grill-with-docs`, `handoff`, `improve-codebase-architecture`, `prototype`,
`research`, `resolving-merge-conflicts`, `setup-matt-pocock-skills`, `teach`,
`to-questionnaire`, `to-tickets`, `triage`, `wait-what`, `wayfinder`, `wizard`,
`writing-for-agents`.

2 from `obra/superpowers-developing-for-claude-code`: `developing-claude-code-plugins`,
`working-with-claude-code`.

`grilling`, `domain-modeling`, `grill-with-docs`, and `wayfinder` — all four used
directly in the session that produced this report — are present and correctly
symlinked into both `~/.claude/skills/` and `~/.codex/skills/`, same as every
other entry on this list. `wayfinder` and `grill-with-docs` carry
`disable-model-invocation: true` in their own upstream frontmatter (explicit-
invoke-only by mattpocock's own design, not a local modification); `grilling`
additionally has its description stripped locally via `skillOverrides` in
`settings.json` (documented, deliberate — see `#60`). None of this affects
whether they're installed correctly, which is what this section checks.

`~/.claude/skills/` (and its mirror `~/.codex/skills/`) additionally carries 4
symlinks with no lockfile entry at all, because they were never installed via the
skills installer — they point into `harness-backup`:

- `consistency-audit`
- `finding-duplicate-functions`
- `rethink`
- `rethink-audit`

This is the same mismatch already tracked in [#51](https://github.com/eranroseman/knowledge-harness/issues/51)
("its README and restore loops still describe three authored skills, while the
tracked tree contains a fourth `finding-duplicate-functions`") — confirmed present,
no new orphans beyond it.

Of these four, three (`consistency-audit`, `rethink`, `rethink-audit`) are
originally authored, no upstream to diff against. The fourth,
`finding-duplicate-functions`, is a stated fork (per the user's own account) of
[obra/superpowers-lab's skill of the same name](https://github.com/obra/superpowers-lab/blob/main/skills/finding-duplicate-functions/SKILL.md)
— missed in the first pass of this sweep, caught on review. Diffed directly
against a fresh clone of `obra/superpowers-lab`:

- `SKILL.md` differs from upstream.
- The upstream implementation is shell-script-based
  (`extract-functions.sh`, `generate-report.sh`, `prepare-category-analysis.sh`);
  the local fork replaced these entirely with a Python implementation
  (`extract-functions.py`, `cluster.py`). This is a substantial adaptation, not a
  drift-sized tweak — squarely what #60's vendoring decision needs to know about.

**Also noted, not chased further (out of scope for the companion, which is about
the global/user-level setup):** `~/memoria-vault` is a separate project with its
own project-scoped plugin config — its `superpowers` install is pinned at a
different commit (`3dcbd5c4b48e02263fbf4a3c01e3fe4f81d584d9`) than the
user-level default (`44c9b2d6e889982ac18c27d05a19fefe335194e1`), and it has its
own `settings.json` and `hooks/` directory. Not diffed — a different vault
entirely, not part of this companion's asset surface.

**On ponytail's hooks specifically** (re-checked directly after a challenge to
this sweep): `.claude-plugin/plugin.json` points at `./hooks/claude-codex-hooks.json`;
the entire `hooks/` directory (`ponytail-activate.js`, `ponytail-runtime.js`,
`ponytail-mode-tracker.js`, `ponytail-config.js`, `ponytail-instructions.js`,
`ponytail-subagent.js`, `ponytail-statusline.sh/.ps1`, `claude-codex-hooks.json`)
was diffed a second time, in isolation, against the exact pinned commit — clean,
byte-identical. `settings.json`'s top-level keys and its full `hooks` block were
also checked directly: no ponytail-specific override or hook customization
exists there, and `CLAUDE.md`/`AGENTS.md` mention ponytail only once each, neither
about a hook. No modification found in the places a hook modification would
live; if a specific one is known, naming the file would let this be checked
precisely rather than by continued search.

## Findings: custom agents

Exactly one: `~/.claude/agents/consistency-audit-inspector.md` — matches the
already-tracked entry (#51), no surprises.

## What this feeds

- [#60](https://github.com/eranroseman/knowledge-harness/issues/60) (vendor changed
  third-party skills): `finding-duplicate-functions` is the clearest vendoring
  case in this whole sweep — a substantially rewritten fork with real provenance
  to record, not a drift-sized tweak. The confirmed candidates beyond that are
  superpowers' two independent divergences (Claude-side README addition,
  Codex-side `AGENTS.md` deletion — neither functional) and whatever
  `skillOverrides` mechanics apply regardless of file content. Ponytail is not
  evidenced as locally changed on either harness by this sweep.
- [#75](https://github.com/eranroseman/knowledge-harness/issues/75) (installed
  plugin/skill disposition): this sweep is the instrument-verified inventory that
  ticket's own body already deferred to instead of a hand-typed list.
