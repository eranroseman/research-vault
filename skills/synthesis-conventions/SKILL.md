---
name: synthesis-conventions
description: Use when creating or editing synthesis notes in a knowledge-harness vault, arranging claims across sources, or asking about synthesis rules
---

# Synthesis conventions

The synthesis layer (`synthesis/`) arranges claims across sources — it asserts arrangement, not evidence. That is why it is freely rewritable: reword, restructure, or reorganize a synthesis note at will. What never moves is the evidence underneath it — every arranged claim keeps citing its source claim link (`[[citekey#^claim-id]]`), never carrying evidence of its own.

## Orientation first

Before creating or editing anything here, read `synthesis/index.md` and the recent `log/` entries. Arrive knowing what topics already exist and what happened recently — never create a page that duplicates one already indexed.

## The 2+-source threshold

A synthesis page earns its existence at two or more sources on the same topic — the only threshold. One source is not yet a synthesis; its claims stay in the literature note until a second source gives them something to arrange against.

## Minimum-link discipline

Every synthesis note carries at least two outgoing wikilinks. A synthesis page with fewer than two links isn't arranging anything yet — it's a stub.

## Index registration

Creating a new synthesis note is not complete until it is registered: add one line for it in `synthesis/index.md`. An unregistered note is invisible to orientation and to anything that later checks the index before creating.
