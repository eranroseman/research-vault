---
name: synthesis-conventions
description: Use when creating or editing synthesis notes in a research-vault vault, arranging claims across sources, or asking about synthesis rules
---

# Synthesis conventions

The synthesis layer (`synthesis/`) arranges claims across sources — it asserts arrangement, not evidence. That is why it is freely rewritable: reword, restructure, or reorganize a synthesis note at will. What never moves is the evidence underneath it — every arranged claim keeps citing its source claim link (`[[citekey#^claim-id]]`), never carrying evidence of its own.

## Orientation first

Before creating or editing anything here, read `synthesis/index.md` and the recent `log/` entries. Arrive knowing what topics already exist and what happened recently — never create a page that duplicates one already indexed.

## The 2+-source threshold

A synthesis page earns its existence at two or more sources on the same topic — the only threshold. One source is not yet a synthesis; its claims stay in the literature note until a second source gives them something to arrange against.

The threshold *permits* a page; it never obligates one. Two sources on a topic make a page allowed, not owed — create one only when the arrangement adds synthesis. Sources set side by side with nothing said about how they relate are a compilation, and a compilation earns no page: leave the claims in their literature notes and say plainly that there was nothing to arrange yet.

## Minimum-link discipline

Every synthesis note carries at least two outgoing wikilinks. A synthesis page with fewer than two links isn't arranging anything yet — it's a stub.

## Frontmatter

A new synthesis note routes through `system/templates/synthesis.md`, substituting its
`{{TITLE}}`/`{{ACTOR}}`/`{{NOW}}` placeholders rather than carrying them verbatim into durable
frontmatter: `{{TITLE}}` is the page's title; `{{ACTOR}}` is the actor per §7 —
`human:<id>` when a person authors the page, `<producer>/<version>` when a skill does; `{{NOW}}`
comes from `python3 -c "from research_vault.notes import generated_at_now; print(generated_at_now())"`.
Never leave a shipped placeholder literal in a written note.

## Index registration

Creating a new synthesis note is not complete until it is registered: add one line for it in `synthesis/index.md`. An unregistered note is invisible to orientation and to anything that later checks the index before creating.
