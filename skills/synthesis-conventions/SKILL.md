---
name: synthesis-conventions
description: Use when creating or editing pages of the compiled layer under wiki/ in a research-vault vault, arranging sources into concept pages, or asking about the rules of that layer
---

# Conventions for the compiled layer

The compiled layer lives under `wiki/` — per-source pages under `wiki/sources/`, cross-source pages under `wiki/concepts/` — and is written by the adopted compile tool (claude-obsidian) through its transaction engine. It asserts arrangement, not evidence: nothing under `wiki/` passes an evidence gate, which is why the folder is the boundary. The evidence underneath it never moves: every page cites its source as `[[<citation key>]]`, which resolves to `literatures/<citation key>.md`, and a page may cite only a source capture wrote — the `captured-set` check fails a commit otherwise.

## Never write the layer by hand

`wiki/` is a machine surface: pages are created and replaced only through the tool's wiki-ingest skill and its `transaction inspect` / `transaction apply` gate. Never `Write` or `Edit` under `wiki/`; the pre-tool-use guard refuses it. Register sources first with `python3 -m research_vault compile KEY --vault PATH` (see `capture-source`).

## Orientation first

Before proposing any page, read `wiki/index.md`, `wiki/hot.md` and the recent `log/` entries. Arrive knowing which concept pages exist and what happened recently — never propose a page that duplicates one already indexed.

## The 2+-source threshold, and the tool's compilation-value gate

A concept page earns its existence at two or more captured sources on the same topic — the vault's one threshold. The tool adds its own gate, which is compatible and stricter: create or expand a canonical page only when the source adds durable synthesis, navigation, a decision, or a reusable connection beyond the source page itself. Two sources set side by side with nothing said about how they relate are a compilation, and a compilation earns no page: say plainly that there was nothing to arrange yet.

## Minimum-link discipline

Every concept page carries at least two outgoing wikilinks, at least one of them a `[[<citation key>]]`. The tool's lint reports orphans (no incoming link) and dead links; both block its checkpoint.

## Frontmatter

The tool's lint requires six keys on every page under `wiki/`: `title`, `type`, `status`, `created`, `updated`, `tags`. `type` is one of the tool's own `PAGE_TYPES` at 32ac5a0 — `source`, `entity`, `concept`, `question`, `comparison`, `session`, `overview`, `meta`, `fold` (`claude_obsidian/page_schema.py`, read 2026-09-16); the vault derives none for `wiki/`. No `{{TITLE}}`-style template exists for this layer any more.

## Index registration

Every canonical page create or removal includes an update to `wiki/index.md` in the same transaction — the tool's rule, and the tool performs it. Never edit `wiki/index.md` by hand; it is the one nested index that legitimately carries frontmatter (ADR 0001, second exemption).

## What is frozen

Claim lines, stance links (`supports`/`disputes`) and claim links (`[[key#^claim-id]]`) are no longer the arrangement's currency; the checks that read them are frozen pending the workflow-component audit. Do not write new ones into `wiki/`.
