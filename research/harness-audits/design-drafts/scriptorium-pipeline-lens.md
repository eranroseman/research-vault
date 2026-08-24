# Scriptorium — a Claude Code Harness for Knowledge Work

## The Pipeline (single-terminal-state chain, gates marked ⛔)

`framing-the-question ⛔brief approved → gathering-evidence → outlining-the-argument ⛔outline approved → claim-driven-drafting (per-claim evidence gate) → fact-check ⛔dual verdict → editorial review ⛔Important issues resolved → filing-a-finished-piece ⛔human picks from fixed menu`

Each skill names exactly one legal successor. No phase starts until the prior phase's artifact is explicitly human-approved, however "simple" the question — the anti-pattern section pre-refutes "it's just a blog post."

## The TDD Analog: Claim-First Drafting

**Iron Law: NO CLAIM ENTERS THE DRAFT WITHOUT A VERIFIED SOURCE FIRST.** Prose written ahead of evidence is deleted, not back-filled.
- **RED:** state the claim and what would falsify it; check the candidate source — watch the claim *fail* against a null/irrelevant source to prove the check has teeth.
- **GREEN:** confirm the source actually supports the claim (page/section level), then write the sentence with its citation attached.
- **REFACTOR:** tighten prose; the mutation check — negate each premise; if no citation would catch the negation, the claim is unprotected: cite or cut.
Rationalization table ports intact: "the abstract is enough," "I remember this statistic," "I'll add citations after drafting" — each rebutted inline.

## What Replaces Tests / Review / Merge

- **Tests passing →** the citation suite: every link resolves, every quote byte-diffs against the original, every number recomputes from raw data.
- **Code review →** fresh-context fact-checker subagent with dual verdicts (claim coverage + prose quality) who is instructed to distrust the drafter's self-report.
- **Merging →** the filing gate: fixed verbatim menu (file to vault / publish / send out / park); deletion only on explicit request plus typed "discard".

## Skill Inventory

| Skill | One-liner | Trigger | Provenance |
|---|---|---|---|
| **using-scriptorium** | Meta-skill: invoke any relevant skill before any response; process skills outrank research skills; rationalization table included | auto, every session | using-superpowers, adapted |
| **framing-the-question** | One-question-at-a-time interview → approved research brief (question, scope, source types, success criteria, out-of-scope) | any new research/writing request | brainstorming, adapted |
| **gathering-evidence** | Parallel source triage: one scout per subtopic, structured summaries with per-claim citations into an evidence ledger | after brief approval | dispatching-parallel-agents + research skill, UNCHANGED core |
| **outlining-the-argument** | Outline-as-plan: each section a task with exact thesis, named sources/quotes, Consumes/Produces claim blocks; "add supporting evidence" is a banned placeholder | after evidence gathered | writing-plans, adapted |
| **claim-driven-drafting** | The Iron Law above | any drafting | test-driven-development, adapted |
| **section-driven-drafting** | Controller dispatches fresh drafter per section; independent fact-checker; capped 5-round fix loop with model escalation; final whole-piece coherence review; append-only research ledger survives compaction | executing an approved outline | subagent-driven-development, adapted |
| **tracing-a-dubious-claim** | Trace the citation chain to the primary source; fix the source note, not the manuscript sentence; three-strikes rule → question the thesis with the human | any fact that looks wrong | systematic-debugging, adapted |
| **verification-before-filing** | No "done" claim without citation-suite evidence in the same message | before any completion claim | verification-before-completion, near-UNCHANGED |
| **requesting/receiving-editorial-review** | Fresh-context reviewer with fixed contract; reception protocol: verify each comment against sources, no "great point!" | after draft complete; on any feedback | code-review pair, adapted |
| **filing-a-finished-piece** | The filing gate menu | pipeline end | finishing-a-development-branch, adapted |
| **draft-isolation** | Revise in a copy/branch after verifying vault health (links resolve, index builds) | before revising living notes | using-git-worktrees, adapted |
| **red-team-my-argument** | Second-model adversarial read: unsupported claims, missing counterarguments, logical leaps; verbatim relay, never auto-applied | user-typed only | codex adversarial-review, adapted |
| **thesis-grilling** | Frontier-in-rounds interrogation of an argument; facts to subagents, decisions to the author | user-typed only | grilling, UNCHANGED |
| **prose-ponytail** | Minimal-writing ladder (link don't restate → citation over summary → one paragraph) with never-cut floor: citations, caveats, provenance; `defer:` markers + debt harvester | auto mode | ponytail, adapted |
| **writing-skills, writing-for-agents, handoff, to-questionnaire, domain-modeling (glossary/ADRs), Strunk, obsidian suite, defuddle, diataxis** | port UNCHANGED — already knowledge-work native | as-is | UNCHANGED |
| **vault-consistency-audit / claim-drift-cron** | Two-reader audit with skeptic refutation; weekly detect-never-apply check for retracted/superseded sources | user-typed / cron | consistency-audit + drift cron, adapted |

## Subagent Roles

**source-scout** (cheap, read-only, `source:page — claim — note` tables), **section-drafter** (mid, brief-only context, 4-status contract), **fact-checker** (mid, gets evidence packet: draft delta + cited passages as files, dual verdicts), **coherence-reviewer** (strongest model, whole piece), **copyeditor** (cheap, Strunk + one reference section). Model tiering: cheap for extraction, strong for synthesis and final review.

## Hooks

- **SessionStart:** load using-scriptorium; inject house-style/citation-policy flag file (re-injected into every subagent, ponytail-style).
- **PostToolUse (Edit/Write on drafts):** regex pass for AI-tells and uncited-number patterns.
- **Stop:** baseline-diff style review of the turn's draft delta; optional **publish gate** — second model answers ALLOW/BLOCK before a piece is marked final, fails closed.

## CLAUDE.md Routing Sketch

~5 lines: process is owned by scriptorium skills (frame→gather→outline→draft→check→file); repo/vault facts live in each vault's AGENTS.md; thesis-grilling is user-typed only (skillOverrides name-only); red-team goes to the second model, never self-applied; drafts live in `drafts/`, cleanup touches only self-owned paths.

## Governance / Settings

`disable-model-invocation: true` on filing, red-team, and grilling (consent-gated actions); internal contract skills `user-invocable: false`; evidence-boundary rule (quote/paraphrase/inference/open-question labels survive every relay) in settings-injected context; harness-backup topology ported UNCHANGED.

## Dropped (YAGNI)

- **caveman token-economy suite** — compression optimizes agentic coding loops; knowledge work's bottleneck is judgment, not tokens (keep only the preserve-floor idea, folded into subagent contracts).
- **wizard** — no recurring human-only portal chores in the core pipeline; re-add per-project if journal submission demands it.
- **ponytail-gain / caveman-stats scoreboards** — no honest baseline exists for "words saved."
- **caveman-init / multi-IDE portability layer** — one harness, one host.
- **codex session-transfer & job broker** — a labeled second-opinion command suffices; ledger infrastructure is overkill for review-shaped delegation.