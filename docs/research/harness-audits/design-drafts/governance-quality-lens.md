# Knowledge-Work Harness — Governance & Quality Lens

Disposition: historical (2026-09-06)

Scope: this lens ports only the verification, economy, and adversarial layers. The brainstorm→outline→draft pipeline belongs to the process lens and is assumed present.

## Skill inventory

| Skill                | One-line                                                                                                                                                                                                                                       | Trigger                                                                    | Port status                                          |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ---------------------------------------------------- |
| `receipts`           | Verification-before-completion for claims: no "done/final" without evidence — every citation resolves, every number recomputed, every quote diffed against source, in the same message                                                         | model-invoked before any completion claim, export, or "ready to send"      | adapted from verification-before-completion          |
| `citation-audit`     | Agentic reviewer traces each claim in a draft to its source note across the vault; flags unsupported claims, secondary-source laundering, broken links                                                                                         | model-invoked at export/publish boundary; user-typed `/citation-audit`     | adapted from security-guidance Layer 3               |
| `epistemic-debt`     | Harvests inline `defer:` markers ("shallow lit search — ceiling: 3 sources, upgrade: before submission") into one ledger; trigger-less markers flagged as rot                                                                                  | user-typed `/epistemic-debt`; model-invoked on "what did we defer"         | adapted from ponytail-debt                           |
| `redpen`             | Cross-model adversarial second reader: attack-surface checklist (unsupported claims, missing counterarguments, citation gaps, logical leaps), 4-part finding bar, schema output with severity+confidence, relayed verbatim, never auto-applied | user-typed only (`/redpen`, `/redpen:adversarial`)                         | adapted from codex:adversarial-review                |
| `thesis-grilling`    | Frontier-in-rounds interrogation of an argument/outline: facts to subagents, every interpretive decision to the author, done only at empty frontier                                                                                            | user-typed only ("grill my thesis", `/grilling`) — name-only override kept | UNCHANGED mechanism, retargeted                      |
| `caveman` suite      | Compressed working dialogue with byte-exact preserve floor (quotes, citations, statistics, negations, qualifiers); persisted prose stays normal                                                                                                | SessionStart hook, `/caveman <level>`                                      | UNCHANGED                                            |
| `margin-notes`       | One-line-per-finding draft review: `p.4 para2: CRITICAL: claim unsupported. cite or cut.` — severity tags, no praise, sentinel "Tight already. Publish."                                                                                       | user-typed `/margin-notes`; model-invoked on review requests               | adapted from caveman-review + ponytail-review        |
| `ruling-book`        | Decision journal: one-paragraph records for hard-to-reverse research choices (scope cuts, framing, corpus exclusions), gated hard-to-reverse AND surprising AND real-trade-off, superseded not deleted                                         | model-invoked when a decision crystallizes                                 | adapted from domain-modeling ADRs + learning-records |
| `vault-audit`        | Two independent readers per concern-slice hunt contradictions, term drift, duplicate claims; every candidate refuted by a skeptic that did not raise it; verdict ledger file; findings triaged agent-fixable / author-must-decide / deliberate | user-typed only                                                            | adapted from consistency-audit                       |
| `receiving-critique` | Editorial-feedback protocol: restate, verify against manuscript and sources, push back with evidence, one comment at a time, no "great point!"                                                                                                 | model-invoked when feedback arrives                                        | UNCHANGED mechanism                                  |

## Meta-skill: `using-standards`

Ports using-superpowers unchanged in structure: loaded every session, forces skill lookup before any response, rationalization table pre-empting scholarly shortcuts ("the abstract is enough", "I remember this statistic", "I'll add citations after drafting" — each with a counter). Governance skills outrank drafting skills; user instructions outrank both. SUBAGENT-STOP exemption kept.

## Hard gates

1. **No claim without a checked source first** (Iron Law; TDD analog). A sentence asserting a fact enters the draft only after its citation is verified against the primary source.
2. **`receipts` before any completion claim** — evidence in the same message, satisfaction phrases banned until then.
3. **Press-check publish gate** (Stop hook, opt-in): second model answers `ALLOW:`/`BLOCK: <reason>` on the final draft; fails closed; manual bypass documented.
4. **Reviewer-never-rewrites**: `redpen`, `margin-notes`, `citation-audit` output findings only; author consents per finding before any change.
5. **Three-strikes thesis rule**: three failed reframings → stop patching paragraphs, question the outline with the human.

## Subagent roles

- **fact-hound** (cheap model, read-only): locates sources, returns `source:page — claim — 6-word note` tables; refusal tokens `not-in-source.` / `ambiguous. ask:`.
- **skeptic-judge** (strong model): adjudicates audit candidates it did not raise; fed raw quotes, never summaries.
- **fresh-eyes reviewer**: sees only brief + draft delta (evidence packet), never session history; must distrust the drafter's self-report; dual verdict (claim coverage + prose quality).

## Hooks

- SessionStart: caveman activation; standards injection; re-inject citation policy into every subagent (ponytail SubagentStart pattern).
- PostToolUse regex on Edit/Write: AI-tell blocklist, uncited-statistic and orphaned-quote tells, injected as warnings.
- Stop: baseline-diff style/claim review of only the changed passages; press-check gate when enabled. Fail-open everywhere except press-check.
- Weekly cron `rot-watch`: detect-never-apply source drift (retractions, dead URLs, superseded datasets); one issue updated in place, filed to the triaged inbox.

## CLAUDE.md routing sketch

Draft review routes through fresh-eyes review; `/margin-notes` is compressed format, invoked by name only. `/redpen` commands carry `disable-model-invocation: true` — offer a second opinion, never assume it ran. `thesis-grilling` gated exactly as today: skillOverrides name-only + prose policy, policy in settings.json never in vendored SKILL.md. Harness-backup versions glossaries, standing audit briefs, citation styles, prompt templates — symlinked directories, copied single files, git status as drift answer.

## Governance/settings

- skillOverrides: `thesis-grilling` name-only; internal contract skills `user-invocable: false`.
- Honest-metrics rule: report only countables (sources verified, words cut, deferrals closed); invented "hours saved" forbidden.
- Evidence-boundary preservation: quote/paraphrase/inference/open-question labels survive every compression and relay.

## Dropped (YAGNI)

- **ponytail-gain scoreboard** — no benchmark corpus for prose; honesty boundary says don't fake one.
- **caveman-init multi-IDE fan-out** — single-user vault, no team tooling to seed.
- **wizard, visual-companion, worktree mechanics** — process-lens concerns, no governance content.
- **caveman-shrink MCP middleware** — no MCP tool-catalog pressure in this workload yet.
- **stop-review-gate for every turn** — kept only as opt-in press-check at publish; per-turn adjudication of prose is noise.
