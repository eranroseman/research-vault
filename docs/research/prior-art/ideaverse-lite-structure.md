# Ideaverse Lite 1.5 — observed vault structure

Disposition: historical (2026-09-06)

Extracted 2026-08-16 from Nick Milo's Ideaverse Lite 1.5 zip (user-provided; archive kept locally at sources/, gitignored for size — 45MB). This is the ACCESS schema's owning artifact in practice, complementing the tweet-derived description in pkm-vault-schemas.md.

## Folder tree (files per folder)

```
    4  (root)
    6  +
   27  .obsidian
 1185  .obsidian/icons
  105  .obsidian/plugins
    8  .obsidian/snippets
   11  .obsidian/themes
  220  Atlas/Dots
   29  Atlas/Maps
    1  Calendar
    2  Calendar/Logs
   15  Calendar/Notes
   13  Efforts/Notes
    4  Efforts/On
    8  Efforts/Ongoing
    2  Efforts/Simmering
    1  Efforts/Sleeping
    1  x
    1  x/Excalidraw
   37  x/Images
    7  x/Templates
```

## Root files

Home.md, Home Basic.md, Ideaverse Map.md, Release Notes.

## Observations material to ticket #7

- Lite 1.5 layout: `+` (inbox) / `Atlas` (Dots, Maps) / `Calendar` (Logs, Notes) / `Efforts` (On, Ongoing, Simmering, Sleeping) / `x` (Templates, Images, Excalidraw).
- Atlas splits **Dots** (220 atomic notes) vs **Maps** (29 MOCs) — not "Sources vs Cards". **No Sources folder exists in Lite**: the evidence-vs-interpretation separation attributed to ACCESS in the schema survey is not enforced by path in this artifact. (Full Ideaverse/Pro may differ — unverified.)
- Efforts encodes actionability as four activity states (On/Ongoing/Simmering/Sleeping) — PARA-like commitment state as folders, but scoped to one branch of the vault rather than the whole vault.
- Bundled plugins (33) notably include dataview, periodic-notes, note-refactor, excalidraw — no citation/reference tooling at all: the template targets general PKM, not academic evidence flow.
