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

| Plugin | Marketplace | Pinned commit | Result |
| --- | --- | --- | --- |
| security-guidance | claude-code-plugins | `6a9c2db` | Clean (verified against exact pin, fetched fresh — marketplace HEAD had drifted) |
| ponytail | ponytail | `2ed6c52` | Clean — no local divergence from the pin found |
| superpowers | superpowers-dev | `44c9b2d` | **Modified**: cache's `README.md` carries a "We're Hiring!" section that the pinned commit's own `README.md` does not contain (confirmed via `git show <pin>:README.md`, zero matches). Content-only (not a skill/hook), and shaped like a stale leftover from an earlier install that an update didn't fully refresh, rather than a deliberate edit — but it is a real, confirmed difference from the pin. |
| caveman | caveman | `3098342` | Clean (verified against exact pin, fetched fresh — marketplace HEAD had drifted significantly, which produced a large false-positive diff before pinning down the real commit) |
| obsidian | obsidian-skills | `a1dc48e` | Clean |
| writing-clearly-and-concisely | agent-toolkit | `3027f20` | Clean |
| diataxis-skills | jrjsmrtn-skills | `e1e15d8` | Clean (this cache dir is itself a git checkout at the pin; `git status --porcelain` shows only the untracked `.in_use` marker) |
| codex | openai-codex | `db52e28` | Clean |
| superpowers-developing-for-claude-code | superpowers-developing-for-claude-code-dev | `74afe93` | Clean |

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

| Plugin | Result |
| --- | --- |
| ponytail | Clean |
| superpowers | **Modified**: `AGENTS.md` is present in the pinned commit but **absent** from the Codex-side cache (confirmed via `git show HEAD:AGENTS.md` in the marketplace clone — the file exists there). A different divergence from the Claude-side one (README addition vs. AGENTS.md deletion) — the two harnesses' copies of the same plugin have drifted from the pin in two unrelated ways. |
| caveman | Clean (only an untracked `.codex-marketplace-install.json` metadata file) |
| obsidian | Clean (only an untracked `.codex-marketplace-install.json` metadata file) |
| writing-clearly-and-concisely | Clean (only an untracked `.codex-plugin` metadata dir) |
| diataxis-skills | Clean |
| codex-security (`openai-curated`) | Not applicable — no `[marketplaces.openai-curated]` entry in `config.toml` and no external git source found; this plugin appears bundled with the Codex CLI itself rather than fetched from a separate pinned upstream, so "diff against pinned upstream" doesn't apply to it. |

`security-guidance`, `openai-codex` (the Claude→Codex bridge itself), and
`superpowers-developing-for-claude-code` are Claude-Code-only and have no
Codex-side counterpart to check.

## Findings: skills reconciliation

`~/.agents/skills/` contains exactly the 20 entries locked in `.skill-lock.json`
(18 from `mattpocock/skills`, 2 from `obra/superpowers-developing-for-claude-code`)
— a perfect 1:1 match, no orphans, nothing missing.

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

## Findings: custom agents

Exactly one: `~/.claude/agents/consistency-audit-inspector.md` — matches the
already-tracked entry (#51), no surprises.

## What this feeds

- [#60](https://github.com/eranroseman/knowledge-harness/issues/60) (vendor changed
  third-party skills): the confirmed candidates for a "changed" vendored copy are
  superpowers' two independent divergences (Claude-side README addition,
  Codex-side `AGENTS.md` deletion — neither functional) and whatever
  `skillOverrides` mechanics apply regardless of file content. Ponytail is not
  evidenced as locally changed on either harness by this sweep.
- [#75](https://github.com/eranroseman/knowledge-harness/issues/75) (installed
  plugin/skill disposition): this sweep is the instrument-verified inventory that
  ticket's own body already deferred to instead of a hand-typed list.
