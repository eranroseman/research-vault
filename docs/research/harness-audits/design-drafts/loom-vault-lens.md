# Loom — a vault-first knowledge-work harness

The vault is the codebase: notes = modules, wikilinks = dependencies, git = history, frontmatter = types, Bases = databases. Every skill below operates on that substrate.

## Meta-skill: `using-loom` [U — ported near-unchanged from using-superpowers]

Loaded every session. Iron rules: invoke any relevant skill before responding; process skills outrank capture skills; no drafting before `charter`; subagents exempt; user outranks skills. Platform reference files map "dispatch a subagent" / "create a todo" to concrete tools.

## The spine (pipeline, single legal successor each)

`charter` → `scaffold` → `weave` → `shelve`

| Skill                                          | From                                                                                                                                                                                                                                                               | One-liner + trigger |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------- |
| **charter** [A: brainstorming]                 | Interviews one question at a time to an approved research brief (question, scope, source types, success criteria, out-of-scope). HARD GATE: no literature search or drafting until approved, however "simple." Trigger: any new research/writing/analysis request. |                     |
| **scaffold** [A: writing-plans]                | Outline-as-plan: each section a task with exact thesis claims, named sources/quotes verbatim, Consumes/Produces blocks (claims relied on vs established), venue constraints copied into every task. "Add supporting evidence" is a banned placeholder.             |                     |
| **weave** [A: subagent-driven-development]     | Controller drafts sections via fresh subagents; independent fact-checker per section; append-only research ledger in the vault survives compaction; 5-round fix cap with model escalation; final whole-document coherence review.                                  |                     |
| **shelve** [A: finishing-a-development-branch] | Fixed menu: merge into vault / send for review / park in drafts. Delete requires typed "discard". Re-checks links resolve post-merge.                                                                                                                              |                     |

## Discipline skills

| Skill                                                    | From                                                                                                                                                                                                                   | One-liner |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| **claim-first** [A: TDD]                                 | Iron Law: no claim enters a draft without a checked citation first — verify the source actually supports it before the sentence exists. Rationalization table ("the abstract is enough," "I remember this statistic"). |           |
| **fact-trace** [A: systematic-debugging]                 | Wrong-looking fact → trace the citation chain to the primary source, fix the source note not the manuscript; three failed reframings of an argument → question the thesis with the human.                              |           |
| **publish-gate** [A: verification-before-completion]     | No "done" claim without evidence in-message: every citation resolves, quotes diffed against originals, numbers recomputed.                                                                                             |           |
| **gardener** [A: ponytail, persistent mode]              | Note-creation ladder, stop at first rung: belongs in an existing note? just a link? one line in the daily note? Never-cut floor: citations, caveats, provenance. `defer:` markers harvested by `/gardener-debt`.       |           |
| **tangle-check** [A: consistency-audit, user-typed only] | Vault audit: two independent readers per slice hunting contradictions, term drift, dead wikilinks; skeptic refutes every candidate; findings triaged agent-fixable / author-decides / deliberate.                      |           |
| **echo-hunt** [A: finding-duplicate-functions]           | Duplicate-note/claim finder; second reader asks "is the difference load-bearing?"; prefer INVESTIGATE over merge.                                                                                                      |           |
| **thesis-grill** [U: grilling, name-only override]       | Frontier-in-rounds interrogation of an argument/outline; user-typed only.                                                                                                                                              |           |
| **lexicon** [U: domain-modeling]                         | Live vault glossary (ontology) with canonical terms, _Avoid_ lists, one-paragraph decision records gated hard-to-reverse AND surprising AND real-trade-off.                                                            |           |
| **devils-reader** [A: codex adversarial-review]          | Cross-model red-team of a draft: unsupported claims, missing counterarguments, logical leaps; schema'd findings, relayed verbatim, never auto-applied.                                                                 |           |

## Vault operations

- **clipper** [U: defuddle + obsidian-markdown] — URL → clean markdown source note, evidence-boundary tags (quote/paraphrase/inference) mandatory.
- **inbox-triage** [A: triage] — reading-inbox state machine (needs-read → verify-against-primary → ready-to-cite / discard); `.out-of-scope/` register of rejected directions prevents re-litigation.
- **obsidian-bases / json-canvas / obsidian-cli** [U] — reading queues, claims trackers, literature matrices as validated .base views; argument maps as canvases with no-dangling-edge checklists.
- **baton** [U: handoff] — session → handoff/daily note, links artifacts by path, suggests next skills.
- **atlas** [U: wayfinder] — multi-session projects as map note + decision tickets, fog-of-war, one decision per session.
- **teach, research, to-questionnaire** [U] — already knowledge work.
- **plainly** [U: writing-clearly-and-concisely] — Strunk + AI-tell blocklist on all human-facing prose.

## Hard gates

1. Brief approval before any search/draft (`charter`).
2. No claim without checked citation (`claim-first`).
3. Publish only with verification evidence (`publish-gate`).
4. Audit findings are reports; human rules per-item before any fix (`tangle-check`).
5. Typed "discard" for deletion (`shelve`).

## Subagent roles

Source-locator (haiku, returns `source:page — claim — note` tables); extractor (1–2 docs, receipt output, refusal tokens `not-in-source.` / `ambiguous.`); section-drafter (fresh context, brief-only); fact-checker (distrusts drafter, dual verdict: claim coverage + prose quality); coherence-reviewer (capable model, final pass). Tiering: cheap = extraction, mid = drafting, top = synthesis.

## Hooks

- **SessionStart**: inject gardener mode + vault conventions; re-inject into subagents.
- **PostToolUse (Edit/Write on .md)**: regex pass — AI-tells, evidence-boundary tags present, wikilink syntax.
- **Stop**: LLM review of draft delta only (baseline snapshot at prompt-submit); optional ALLOW/BLOCK publish gate via second model, fail-closed.
- **Cron `source-watch`** \[A: drift-check\]: weekly — retracted papers, dead URLs, superseded datasets; detect-never-apply, one in-place issue into the inbox.
- **Cron `weekly-tend`**: periodic review — orphan notes, unprocessed inbox, stale `defer:` markers → one daily-note report.

## CLAUDE.md routing sketch

~6 lines: process owned by Loom skills; vault facts/policy live in the vault's own AGENTS.md note; `thesis-grill` explicit-request-only (backed by settings.json name-only override, never in vendored SKILL.md); `tangle-check`/`devils-reader` user-typed only; worktree analog = draft branches, cleaned explicitly; harness-backup symlinks vault config + skills, copies single files.

## Governance

`disable-model-invocation` on destructive/consent-heavy ops; internal contract skills `user-invocable: false`; hooks fail-open, never block a session; style-policy files additive-only (can tighten, never waive house style); honest metrics only (counted merges/words-cut, no invented "hours saved").

## Dropped (YAGNI)

**wizard** (no credential dashboards in PKM), **prototype/UI variants** (keep only outline-it-thrice as a `scaffold` option), **resolving-merge-conflicts** (rare; fold into `shelve`), **caveman channel-compression suite** (keep only the preserve-floor rule — negations, numbers, quotes byte-exact — inside subagent contracts; a full token-economy plugin isn't worth its overhead for prose sessions), **caveman-init/ponytail portability layer** (single-host vault), **security-guidance regex corpus** (replaced by prose/citation checks), **run/dataviz dev tooling** (no app to launch).
