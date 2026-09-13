# Vendoring the compile tool's prose

This project will not fork or vendor `AgriciDaniel/claude-obsidian`'s prose
surface — its `skills/`, `agents/`, `WIKI.md` and `templates/` — in order to
bend its research methodology toward PRISMA-S, PRISMA-ScR, or the
notetaking-for-historians method.

## Why this is out of scope

The tool splits cleanly in a way that invites exactly this. Its Python core does
two things: it renders a template tree once, and it validates agent-authored
transaction bundles against path-scope, hash-precondition and schema rules.
Everything else — page bodies, frontmatter values, index entries, `sources:`
backlinks — is written by an LLM following prose. Adopt the engine, rewrite the
prose, and you appear to get a methodology-aware wiki for the price of some
editing.

The upstream release model forbids it economically. Measured at pin `ad67087`
on 2026-09-07:

- of **49 prose files, zero were unchanged** across 90 days
- turnover is **2.06×** overall, and **2.85×** on the mixed methodology files —
  the ones worth owning
- **98.5% of that churn arrived in a single release-promotion commit** of
  81,000+ lines

The public repository is a distribution mirror populated wholesale from a
private tree. `README.md:307-310` says so: *"A public default branch must be
populated from that audited tree, never by pushing contributor-vault state."*
A fork therefore never merges reviewable diffs. At each release it faces a
whole-tree replacement and must re-derive its adaptations against rewritten
files — roughly **2,800 conflicting lines per cycle** on the 957-line subset
worth adapting, and there was one such cycle in the 90-day window.

There is no supported seam to use instead. Verified by grep, all returning
nothing: `"custom scaffold"` is prose pointing at prose with no code reading a
profile; `extensions.py` is legacy compatibility with one function; modes are a
closed four-value enum; and no config key anywhere names a prose file.

Two of the highest-value methodology files also have a Python ceiling, so
vendoring would not even reach them. `provenance.md`'s authority tiers and
review states are closed enums in `ledgers.py:25-49`, code-validated — a
PRISMA-S screening stage cannot live in the source ledger without patching
Python, whatever the prose says.

## What is in scope instead

- **Adopting the tool unmodified** and driving it through a wrapper of our own,
  so upgrading is `git pull` with no conflict surface and every line we
  maintain is ours.
- **Expressing methodology in free-form frontmatter values and page
  structure**, which the tool permits: its lint checks that six keys exist and
  never validates what they hold.
- **Letting lane 4 supply the method.** It curates research skills against
  exactly these floors, so a curated skill carrying PRISMA-S would make bending
  this tool's prose work nobody needed to do. Lane 5's gap pass is where a
  surviving gap would show up.

## Prior requests

- Proposed and rejected in the ingest redesign session of 2026-09-07. No issue
  was filed: the decision has a home in
  [the ingest spec §4.3](../docs/superpowers/specs/2026-09-06-import-redesign-design.md),
  and the tracker is for findings with no home.
