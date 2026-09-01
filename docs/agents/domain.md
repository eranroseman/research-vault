# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root, or
- **`CONTEXT-MAP.md`** at the repo root if it exists — it points at one `CONTEXT.md` per context. Read each one relevant to the topic.
- **`docs/adr/`** — read ADRs that touch the area you're about to work in. In multi-context repos, also check `src/<context>/docs/adr/` for context-scoped decisions.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The `/domain-modeling` skill (reached via `/grill-with-docs` and `/improve-codebase-architecture`) creates them lazily when terms or decisions actually get resolved.

## File structure

Single-context repo (most repos):

```
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

Multi-context repo (presence of `CONTEXT-MAP.md` at the root):

```
/
├── CONTEXT-MAP.md
├── docs/adr/                          ← system-wide decisions
└── src/
    ├── ordering/
    │   ├── CONTEXT.md
    │   └── docs/adr/                  ← context-specific decisions
    └── billing/
        ├── CONTEXT.md
        └── docs/adr/
```

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal — either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007 (event-sourced orders) — but worth reopening because…_

## This repo's ADR authoring rules

Distilled 2026-09-01 from the transcript archive (#68 mining; provenance:
`a89fa797` @ 2026-08-24, `2e6f1385` @ 2026-08-24) — the shape rules behind the accepted ADRs
(13–33 lines), which were ruled in-chat and never written down. The ADR bar itself is the
domain-modeling skill's three tests; these rules govern *content*, not admission:

- Cut what a reader working in this repo already knows; ADRs carry only what a cold reader
  must be told.
- Never cite a record the reader cannot open — assert borrowed reasoning on its own merits
  ("the reference to memoria and its ADRs will be meaningless to the reader").
- The title states the decision, not a truism ("# Human gates only where judgment can differ"
  was rejected: "doesn't really say anything").
- ADRs carry no history: no change logs, no provenance narratives, no "(revised after…)"
  status lines. Git history holds that; the file restates a lookup.
- Prefer one sentence in an existing ADR or the vault AGENTS.md over a new file ("better
  adding a single sentence to an ADR than being locked to a useless ceremony").
- A correction of an agent's mistake is not a decision. Cheap test: "would this decision
  exist if the agent had simply done the obvious thing?" If not, it is a correction — it
  belongs in the skill/AGENTS.md the agent loads, not in an ADR.
- Routing doctrine: rules agents follow go where agents read them; invariants code must hold
  go in tests that name the reason; an ADR is only for a choice a future designer would
  otherwise reverse without knowing what it cost.
