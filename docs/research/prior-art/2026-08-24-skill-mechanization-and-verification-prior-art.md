# Prior art: mechanizing prose rules, verifying LLM verification, and multi-agent reliability

**Verdict (2026-08-24, dispositions routed):** Five adoptions, all polish-tier, zero new dependencies — independence-collapsed source counting + `confidence-present` (→ polish item 12), the four-state canonical table in `evidence-conventions` with per-surface deltas and the settled "four-state honesty" token (→ item 14), unconditional `redact_url` inside the `search-log` verb (→ item 18), the token-ordered quote matcher (→ item 19), routing/firing fixtures in the skill-eval lane (→ item 11). One pre-registered measurement: §B's CoVe second pass runs at slice Phase 5 as a disagreement-rate base-rate pilot, not a standing default — the 2× cost is unpriced until then. Two findings point at already-registered triggers rather than new records: §C's debate passes are the named tune if the slice's measured integrate-hold precision collapses (warn-tier precision doctrine), and D2's severity field is already in Plan S's Memoria-item map. One investigate-first: D3's UNREACHABLE recheck (→ item 20 — the gap may be narrower than stated, since `verify` re-runs every check per invocation). Declined with revisit conditions: the router skill (the vault AGENTS.md routing index is this repo's shipped answer; revisit on slice orientation friction) and find-sources parallel dispatch (real, shipped precedent, but Phase 3's volume doesn't need it — the post-slice friction map governs).

Research note, 2026-08-24. Grounds three core improvement directions identified against this repo's
skill set — mechanizing prose rules that have a checkable predicate (§A), verifying an LLM pass's
own verdicts before trusting them (§B), and multi-agent decomposition for single-shot judgment calls
(§C) — in named, primary-sourced prior art, so a future implementation cites real precedent rather
than reinventing it. Five skills are the direct target of §§A-C:
`skills/synthesis-conventions/SKILL.md`, `skills/factcheck-draft/SKILL.md`,
`skills/import-source/SKILL.md`, `skills/project/SKILL.md`, `skills/find-sources/SKILL.md`. Two
further sections extend past that scope: §D names gaps that cut across skills outside the original
five, with a thinner evidence tier than A-C; §E names specific passages worth adapting directly
rather than reimplementing.

Organized by practice, not by when each piece was found. For each practice, evidence comes in
three tiers, always in the same order: **published** (academic papers, Anthropic's own engineering
posts), **shipped and comparable** (this repo's own verified product-landscape research,
`docs/product-landscape/2026-08-22-product-comparison-verified.md`, file-level-read competitor
skill systems), and **shipped and running** (`obra/superpowers`, the process-skill framework this
very session runs on — vendored locally at
`/home/eranr/.claude/plugins/cache/superpowers-dev/superpowers/6.2.0/skills/`, confirmed via both
WebFetch and `gh api repos/obra/superpowers/contents/skills` to match the live `main` branch's
14-skill list with no drift as of 2026-08-24). Every claim below is read from the primary source
directly, quoted rather than paraphrased from a secondary summary, with a URL, arXiv identifier, or
repo-relative path.

## Summary

**§A — mechanize prose only where a script can check it from outside the agent's own reasoning.**
`synthesis-conventions`'s "2+ sources" / "2+ links" rules, `find-sources`'s prose-only
credential-redaction fallback, and a `[confidence:: ...]` field nobody checks for presence are all
externally-checkable predicates left as prose while structurally identical rules elsewhere in this
repo already have a `check_id`. A fourth instance is a duplication, not a missing check: four skills
(`factcheck-draft`, `publish`, `verify-citations`, `import-source`) each independently restate the
same four-state result table, worded differently every time, with no canonical version anywhere.
This is **policy-as-code** (OPA) applied at the agent-instruction layer, per Anthropic's own
Skill-authoring "degrees of freedom" doctrine. It has a real boundary, though: `obra/superpowers`'s
own `verification-before-completion` and `systematic-debugging` enforce their rules entirely through
bulletproofed prose, deliberately, because what they check — did the agent actually run the command
this turn — has no face a script outside the agent's turn can inspect.

**§B — don't trust a single LLM pass's own verdict.** `factcheck-draft` runs one LLM adjudication
per claim with no check on its own MATCHED result. **Chain-of-Verification**, **self-consistency**,
**SelfCheckGPT**, and **LLM-as-judge** all name a second, independent pass as the fix — and
pedrohcgs/claude-code-my-workflow has already built exactly this as a forked-context Claude Code
subagent, the strongest single citation in this report because it answers the implementation
question the papers leave open. A complementary lever shrinks the problem instead of double-checking
it: this repo's own quote matcher is contiguous-only, where a comparable product's token-ordered
matcher catches cases (a superscript or line number landing mid-sentence) that today force an
LLM-level judgment call for what is really a parsing gap.

**§C — a single subagent's judgment call needs a second, adversarial one before it's trusted.**
`import-source`'s contradiction/confidence holds, `project`'s gap-analysis buckets, and
`find-sources`'s single-database-at-a-time routing are each one-shot judgment. **AI safety via
debate**, **multiagent debate for factuality**, and Anthropic's own multi-agent research system (a
measured 90.2% quality gain from subagent separation) name this pattern; `obra/superpowers`'s
`subagent-driven-development` and `dispatching-parallel-agents` already run it as this session's own
default, with the round-cap, escalation, and park-not-drop mechanics the academic papers leave
abstract.

**§D — three more gaps, thinner evidence, plus a testing note.** No test checks that the right skill
actually *fires* for realistic phrasing — only that each `SKILL.md` file is well-formed. Findings
carry no severity, so a trivial and a serious instance of the same check are indistinguishable to the
gate. And an UNREACHABLE result today has no mechanism that brings the check back once the outage
clears — "never a verdict" is enforced, but nothing schedules the retry. Unlike A-C, none of these
three have a published-paper or shipped-and-running tier behind them — shipped-and-comparable only
(gbrain, medsci, research-hub) — noted explicitly rather than left silent. Separately: none of A-C's
own fixes have been pressure-tested per this repo's own vendored `writing-skills` methodology before
being trusted.

**§E — six passages already read this session, concrete enough to adapt directly into this repo's
own skills, not just cite as precedent** — a dispatch rule, a fix-loop procedure, a context-isolation
rule, a discipline-prose format, a router-skill pattern, and a term-compression technique, each
pointing at the exact file and the exact skill it fits.

______________________________________________________________________

## A. Mechanize prose with a checkable predicate

**The gap.** `skills/synthesis-conventions/SKILL.md` states two binding, numerically precise rules —
"A synthesis page earns its existence at two or more sources on the same topic" and "Every synthesis
note carries at least two outgoing wikilinks" — as pure prose. A grep of `research_vault/lints.py`
confirms `check_id`s exist for `citekey`, `evidence-layer`, `published-drift`, and `disputed-claim`,
but none for synthesis's source-count or link-count rules — every other rule in the system has both
a prose description and a machine-enforced check; these two do not. `skills/find-sources/SKILL.md`
has the same shape for a different rule: step 5 says its bundled `redact_url` helper "strips
`api_key`/`email`/`mailto`/`tool` values" from URLs, but only for calls routed through the bundled
scripts — for anything else, the skill's own text is "do the same by hand for anything you don't run
through it." A mechanical guarantee for the scripted path, prose discipline for every other path.

**Policy-as-code (OPA).** "You specify policy as code and simple APIs to offload policy
decision-making from your software... OPA decouples policy decision-making from policy enforcement"
(https://www.openpolicyagent.org/docs, read 2026-08-24). The generalizable claim isn't OPA-the-tool
— it's the separation it names: a policy stated as code that a mechanical evaluator enforces, kept
apart from the system whose behavior it governs.

**Anthropic's Skill-authoring doctrine.** The official best-practices doc gives an explicit decision
rule for prose versus code: "Match the level of specificity to the task's fragility and
variability," with **low freedom** called for when "Operations are fragile and error-prone" and
"Consistency is critical" — illustrated with a "narrow bridge with cliffs on both sides: There's
only one safe way forward." It separately states: "**Prefer scripts for deterministic operations:**
Write `validate_form.py` rather than asking Claude to generate validation code"
(https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices, read 2026-08-24).
A binary numeric threshold ("2+", "2+") is definitionally the narrow-bridge case: one right answer,
zero legitimate variation. The companion tools-for-agents post states the same move at the interface
layer — designs should "offload agentic computation from the agent's context back into the tool
calls themselves. This reduces an agent's overall risk of making mistakes"
(https://www.anthropic.com/engineering/writing-tools-for-agents, read 2026-08-24) — read generally,
this is exactly what the redaction gap needs too, though a redaction-specific search of that same
article (full-text, for "secret," "credential," "API key," "PII," "sanitiz," "mask," "redact,"
"sensitive," "leak," "expose") found none of those terms; that gap's naming leans on this same
general doctrine rather than new material.

**The boundary: when prose is correct instead.** `obra/superpowers`'s `verification-before-completion`
and `systematic-debugging` hold their core rule entirely in prose, deliberately.
`verification-before-completion`'s Iron Law — "NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION
EVIDENCE" — is backed only by a rationalization table ("'Should work now' | RUN the verification")
and a red-flags list; its directory contains exactly one file, no script, no lint, no CLI.
`systematic-debugging`'s Iron Law carries the same shape; its directory does hold
`find-polluter.sh`, a bisection script, but that tool helps the agent investigate — it does not gate
the agent on having investigated. The phase-ordering rule itself stays prose in both.
`obra/superpowers`'s own `writing-skills` names the reason: its "Match the Form to the Failure"
table prescribes "Prohibition + rationalization table + red flags" for a failure that "Skips/violates
a rule under pressure (knows better, does it anyway)," versus a structural fix for a failure that
"Omits a required element from something they already produce." `verification-before-completion` and
`systematic-debugging` are the first class — the predicate being checked (did you actually run the
command this turn) is what happened inside the agent's own turn, not a property of a file a script
can open afterward. `synthesis-conventions`'s "2+ sources, 2+ links" is the second class —
externally checkable from a file already on disk. Test any future mechanize-or-not candidate against
that same question before assuming policy-as-code applies.

**Writing the fix, and a fifth instance found this way.** This repo's own `writing-for-agents` skill
(`/home/eranr/.agents/skills/writing-for-agents/SKILL.md`) supplies two more points once a check
exists. First, a token-economy argument for the same fix, independent of policy-as-code: "The
environment is a source of truth too... a document that restates it is a cache... Cache what the
agent cannot find by looking... Leave the one-file, one-command lookups to the environment, where
they cannot go stale" — once `synthesis-conventions` has a `check_id`, its SKILL.md prose should
point at the check rather than restate the threshold, a stale-prone cache of something the check
reports cheaply and current. Second, on how to word any of this report's fixes generally: "steering
by prohibition drags the forbidden behaviour into context and makes it more available, not less...
Prompt the positive" — independently converging, by an attention/priming argument rather than
`writing-skills`'s measured wording tests, on the same conclusion: state what a check does and what
MATCHED/UNMATCHED reporting looks like, not a list of what not to claim. Third, a concrete instance
this convergence caught directly: a grep of `skills/*/SKILL.md` for `MATCHED` shows `factcheck-draft`
(lines 66-73), `publish` (33-40), `verify-citations` (23-34), and `import-source` (154-161) each
independently restating their own four-row MATCHED/UNMATCHED/UNREACHABLE/SKIPPED table, worded
differently every time, while `skills/evidence-conventions/SKILL.md` — the shared-vocabulary skill
all four already route to — holds no canonical version (`grep -n "four-state"` there returns
nothing). "Duplication — the same meaning in more than one place — costs maintenance and tokens" is
`writing-for-agents`'s own name for this: a fifth instance of this section's class of finding, not a
missing check this time but a missing single statement.

**A sixth instance: `[confidence:: ...]` presence is unchecked.** `evidence-conventions`'s
synthesis-only field `[confidence:: <level>]` (inference-only) has no `check_id` validating that an
inference claim actually carries it — confirmed directly: `grep -rn "confidence" research_vault/*.py` finds the string only once, as a reason code (`inbox.py:28`), never as a
check. hermes/llm-wiki "makes a missing confidence field a lint signal"
(`docs/product-landscape/2026-08-22-product-comparison-verified.md:1628-1629`). This splits cleanly
from §C's already-covered judgment question (is the value *low*) — presence-of-field is mechanical,
the same shape as this section's other five instances.

**Sharpening fix (1): count independent sources, not just citations.** Once `synthesis-conventions`
has its check_id, "2+ sources" as specified would still pass on two papers by the same author, or
one citing the other. claude-obsidian's `_independent_group_count()` "collapses sources sharing an
origin, content hash or independence key so they cannot count as independent corroboration"
(`docs/product-landscape/...:360-365`) — fold this into the same check rather than treating it as a
separate gap: count distinct independent sources, not a raw citation count.

**Example — the pattern already exists, just not for these rules.** `verify-citations/SKILL.md`
already describes the exact report shape a `synthesis` check_id would reuse: "`verify` prints one
line per non-MATCHED outcome — `RESULT check target — reason` — followed by a final JSON summary of
counts by result," invoked as `python3 -m research_vault verify --vault PATH`. Nothing new to
design — `synthesis-source-count`/`synthesis-link-count` slot into that same reporting shape
`citekey` and `evidence-layer` already use.

**Fixes.** (1) Add a `synthesis` check_id (or two — `synthesis-source-count`,
`synthesis-link-count`) to `research_vault/lints.py`/`verify.py`, reporting MATCHED/UNMATCHED
exactly as `citekey` and `evidence-layer` already do, counting *independent* sources per the
sharpening above, then trim the SKILL.md prose to state the rule and route to the check. (2) Remove
`find-sources`'s "by hand" branch entirely by routing every URL that reaches the search log or a
report through `redact_url` unconditionally — most naturally from inside the `search-log` CLI verb
itself, so an un-redacted URL cannot be appended regardless of which call produced it. Concretely,
the verb `find-sources/SKILL.md` already documents —

```sh
python3 -m research_vault search-log --vault PATH --project NAME \
  --query "QUERY AS RUN" --source "DATABASE NAME" --hits N
```

— is where `redact_url` should run unconditionally on every argument before the line is written,
rather than the skill telling the agent to have already redacted by the time it types this command.
(3) Collapse the four-state table's four copies into one disclosed reference inside
`evidence-conventions` (already the shared-vocabulary skill the other four route to), with each of
the four keeping only what's actually different at its call site — e.g. `factcheck-draft`'s row
today reads "**MATCHED** writes nothing. Factored verification is LLM judgment... so a clean
adjudication has no durable record to write," while `import-source`'s reads "**MATCHED** | The check
ran and agreed. Only the CLI's deterministic checks mint a `verified` event" — same meaning, two
independent sentences; one canonical version in `evidence-conventions` replaces both. (4) Add a
`confidence-present` check_id alongside (1), same shape, for the sixth instance above — the field it
checks for is exactly the one `evidence-conventions/SKILL.md` already syntaxes: "**`[confidence:: <level>]`** — inference-only."

## B. Verify the verifier: don't trust a single LLM pass

**The gap.** `skills/factcheck-draft/SKILL.md` runs "factored verification": one LLM pass checks
each selected claim against its cited source and records MATCHED/UNMATCHED/UNREACHABLE/SKIPPED. A
MATCHED result "writes nothing" and is reported directly — there is no second check on whether that
verdict itself was correct.

**Named techniques.** **Chain-of-Verification** states the method as four steps, the load-bearing
one being independence: the model "answers those questions independently so the answers are not
biased by other responses" (Dhuliawala et al., arXiv 2309.11495). **Self-consistency** replaces
greedy decoding with sampling multiple reasoning paths and "selects the most consistent answer by
marginalizing out the sampled reasoning paths" (Wang et al., arXiv 2203.11171) — applied here, run
the same adjudication N times independently and require a majority before treating a claim as
settled. **SelfCheckGPT** needs no reference source at all: "for hallucinated facts, stochastically
sampled responses are likely to diverge and contradict one another" (Manakul et al., arXiv
2303.08896) — the right fit specifically for `inference`-tagged claims, where the adjudication
itself is a judgment call with no source text to byte-compare against; sample it multiple times and
treat divergence as its own signal. **LLM-as-judge** is the direct precedent for a second,
separately-prompted verdict pass, but its own caveat matters here: "position, verbosity, and
self-enhancement biases" mean the same model checking its own verdict is weaker evidence than an
architecturally distinct judge (Zheng et al., arXiv 2306.05685) — relevant because the cheapest
implementation of any of these fixes (same model, same context, asked twice) is exactly the setup
the paper flags as unreliable. **Self-Refine** is a negative precedent, not a fix: its single-model,
single-context loop — "the same LLM provides feedback for its output and uses it to refine itself"
(Madaan et al., arXiv 2303.17651) — is exactly `factcheck-draft`'s current unaudited shape; it
describes the failure mode, and lacks the independence boundary every fix above has. **RARR** (Gao
et al., arXiv 2210.08726) and **FActScore** (Min et al., arXiv 2305.14251) are weaker fits for this
gap specifically, noted in Dead ends below.

**Already shipped, not only published.** pedrohcgs/claude-code-my-workflow's `verify-claims` "runs
Chain-of-Verification per Dhuliawala et al. 2023, spawning a `claim-verifier` agent in a forked
context so the verifier never sees the draft" (`docs/product-landscape/2026-08-22-product-comparison-verified.md:467-478`)
— CoVe's exact independence requirement, already built as a Claude Code subagent using the same
primitive this repo already has, not merely proposed in a paper. This is the strongest single
citation in this report for this gap. Imbad0202/academic-research-skills' "cross-model verification
against Codex" (`docs/product-landscape/...:247-259`) is the strictly stronger version: a check run
on a structurally different model removes the self-enhancement-bias risk Zheng et al. flag, rather
than merely mitigating it.

**This session's own default.** `obra/superpowers`'s `requesting-code-review` states the same
independence rule as a general dispatching principle, not one paper's technique: "The reviewer gets
precisely crafted context for evaluation — never your session's history"
(`skills/requesting-code-review/SKILL.md`) — a third, converging source for the same requirement.

**Fix.** Before a MATCHED verdict short-circuits to "report to person, write nothing," run one
CoVe-shaped independent second pass — fresh subagent context, no visibility into the first verdict,
per pedrohcgs's already-shipped pattern and this session's own `requesting-code-review` default — or,
budget permitting, self-consistency's N-sample-and-majority. Restrict it to the highest-stakes tag
(`inference`; `paraphrase` is comparatively checkable and `quote` is already deterministically
covered). A disagreement between the two passes files as `UNMATCHED` with a reason code naming the
disagreement — never silently resolved in either direction. No new recording mechanism needed:
`factcheck-draft/SKILL.md` already documents exactly this shape for every other UNMATCHED outcome —

```sh
python3 -m research_vault finding factcheck CLAIM_LINK UNMATCHED "mismatch — ONE-LINE REASON" --vault PATH --target-hash TEXT_HASH
```

— a second-pass disagreement is one more `mismatch —` reason on the same call, not a new verb.

**A complementary lever: shrink what needs the LLM pass at all.** The fix above adds a second
judgment; this finding removes some claims from needing a first one. "medsci answers 'does the
source say what the sentence claims' in code rather than by LLM adjudication... On quote matching
the gap is narrower than it first appears: our `selectors._norm_with_map` already normalises NFKC
drift, soft hyphens, line-break hyphenation and whitespace against extracted PDF text, but matches
contiguously, so a line number or a superscript landing mid-sentence still breaks it. medsci's
token-ordered subsequence match does not"
(`docs/product-landscape/2026-08-22-product-comparison-verified.md:1556-1561`). Fix: port a
token-ordered subsequence matcher (medsci's `_ordered_run(needle, hay, allow_missing)`, already
described in this repo's own research as "the class our contiguous find misses") alongside
`_norm_with_map`, so fewer `quote` claims ever reach an LLM adjudicator with a false mismatch —
`verify-citations`' deterministic `quote` check gets more precise, and the LLM-verification burden
above shrinks by exactly the cases the current matcher gets wrong for a reason that has nothing to
do with whether the claim is true.

## C. Multi-agent decomposition for single-shot judgment calls

**The gaps.** `skills/import-source/SKILL.md` §4 asks a single pass of judgment to decide, per
newly-imported claim, whether it's a contradiction, low-confidence, or a schema violation — one-shot,
no second opinion. `skills/project/SKILL.md`'s gap-analysis step similarly sorts findings into
covered/contested/missing in one pass. `skills/find-sources/SKILL.md` step 2 routes every query to
one primary database at a time, and step 5's "serialize requests to any one rate-limited host" — a
rule about *within*-host ordering — is never paired with any instruction about *across*-host
parallelism, so a query that legitimately spans several databases still runs as one agent, one query,
one database at a time.

**Named techniques.** **AI safety via debate**: "two agents take turns making short statements... then
a human judges which of the agents gave the most true, useful information" (Irving, Christiano,
Amodei, arXiv 1805.00899) — judgment improves when one side of an exchange is structurally
incentivized to find the flaw, rather than a single agent grading its own homework. **Multiagent
debate for factuality** operationalizes the same idea without a human judge: "multiple language model
instances propose and debate their individual responses and reasoning processes over multiple rounds
to arrive at a common final answer," reducing "fallacious answers and hallucinations" (Du et al.,
arXiv 2305.14325) — fully agent-to-agent, directly implementable as two subagent invocations
exchanging positions before the caller accepts a verdict. **Anthropic's own multi-agent research
system** is the primary source for this repo's actual architecture: "a lead agent coordinates the
process while delegating to specialized subagents that operate in parallel," measuring "a multi-agent
system... outperformed single-agent Claude Opus 4 by 90.2%," because "each subagent also provides
separation of concerns — distinct tools, prompts, and exploration trajectories — which reduces path
dependency," including a dedicated `CitationAgent` isolating citation-correctness as its own role
(https://www.anthropic.com/engineering/built-multi-agent-research-system, read 2026-08-24). The same
post supports `find-sources`'s gap directly: "the lead agent spins up 3-5 subagents in parallel rather
than serially," each given "guidance on the tools and sources to use," cutting "research time by up to
90%" — illustrated by a worked example where a single agent failed a multi-part query with "slow,
sequential searches" that a decomposed multi-agent system solved. One caveat: the article never states
in so many words that parallel subagents query *different databases* — that mapping is this report's
own structural inference from its general parallel-tool-use language, not a verbatim claim.
**"Building Effective Agents"** names two matching workflow shapes: **orchestrator-workers** ("a
central LLM dynamically breaks down tasks, delegates them to worker LLMs, and synthesizes their
results") fits `project`'s gap analysis, and **evaluator-optimizer** ("One LLM call generates a
response while another provides evaluation and feedback in a loop") fits the contradiction/
confidence/schema classification (https://www.anthropic.com/engineering/building-effective-agents,
read 2026-08-24). **Mixture-of-agents** is named for completeness in Dead ends below.

**Already shipped, not only published.** AgriciDaniel/claude-obsidian's `agents/verifier.md` is "a
fresh-context, read-only verifier subagent (`model: sonnet`, `maxTurns: 35`, tools `Read, Grep, Glob, Bash`)" that "reports evidence-ranked findings without modifying Git or repository state"
(`docs/product-landscape/...:339-368`) — a concrete, reusable template: fresh-context independence
plus a *tool-permission* boundary, where the verifier isn't merely told not to write, its tool list
makes writing impossible. nvk/llm-wiki "launches 5, 8 or 10 parallel agents by depth" (`...:487-494`)
— precedent for scaling subagent count to the task rather than a fixed number, relevant to sizing
`find-sources`'s per-database dispatch to however many rows a query spans. This repo's own
product-landscape research already names the gap directly: "Our skills are single-threaded"
(`docs/product-landscape/...:1723-1726`), against five comparable products that have already closed
it five different ways. huytieu/COG-second-brain's "V-model verification lifecycle where the worker
never grades its own homework" independently converges on the same framing as Self-Refine's failure
mode (§B), flagged at the source's own lower ◐ (tree-listed, not file-read) confidence tier — see
Dead ends below.

**This session's own default.** `dispatching-parallel-agents` states `find-sources`'s exact fix
verbatim: "Dispatch one agent per independent problem domain. Let them work concurrently... Issue
all... dispatches in the same response — they run in parallel... Multiple dispatch calls in one
response = parallel execution. One per response = sequential."
(`skills/dispatching-parallel-agents/SKILL.md`) — not a description of the mechanism, the literal
mechanism already governing this session's own subagent dispatches. `subagent-driven-development`
supplies the mechanics the debate papers leave abstract: reviewer isolation ("They should never
inherit your session's context or history"), realized as a diff file rather than the implementer's
reasoning; a round cap and escalation rule ("Rounds 1-3 — resume the original implementer... Rounds
4-5 — dispatch a fresh implementer on a more capable model"); adjudication withheld until the cap
("Adjudicate only at the cap. Adjudicating earlier to end a loop is pre-judging with a different
name"); and unresolved-but-not-load-bearing findings parked rather than dropped ("park it — `Task <N>: parked — <finding> — ruling: <why the code stands>`. The final review sees both sides.")
(`skills/subagent-driven-development/SKILL.md`).

**Fixes.** For `import-source`'s three hold conditions and `project`'s gap analysis: keep the first
pass as-is, add a second, independently-prompted subagent whose sole job is to argue the opposite
verdict — Irving et al.'s debate shape — adjudicated by the calling agent using
`subagent-driven-development`'s round-cap/escalation/park mechanics rather than trusted from one
pass; `project`'s classification additionally fits Anthropic's orchestrator-workers shape, dispatched
per synthesis-page-cluster rather than sorted in one pass over the whole bibliography. For
`find-sources`: when a query genuinely spans more than one row of the routing table, dispatch one
subagent per database — each handed the same objective and its `references/*.md` file (already
matching the shape Anthropic's post asks each subagent to be given) — sized to nvk's depth-scaling
precedent and using `dispatching-parallel-agents`'s same-response dispatch rule; each subagent still
logs its own line through the unmodified `search-log` verb, and a caller-level merge presents the
combined candidates once. The recording verb for the debate outcome already exists too —
`import-source/SKILL.md` files a held claim as

```sh
python3 -m research_vault finding integrate CLAIM_LINK UNMATCHED "contradiction — ONE-LINE REASON" --vault PATH
```

— an adjudicated debate verdict is the same call, with the reason naming which side the calling
agent found persuasive, not a new finding shape.

## D. Three more gaps, outside A/B/C, plus how to trust the fixes above

Unlike A/B/C, the three gaps below only carry the shipped-and-comparable tier (gbrain, medsci,
research-hub) — no academic paper and no `obra/superpowers` precedent were found for any of them, so
the three-tier pattern this note otherwise follows doesn't apply here; noted rather than forced.

**Skill-routing evaluation — no test checks that the right skill actually fires.**
`tests/test_skill_contracts.py` and `test_skill_files.py` check that each skill's frontmatter
parses, its name matches its directory, its description is non-empty, and every identifier it cites
exists — testing the *file*. "None of it tests the *firing*: given a phrasing a researcher would
actually use, does the right skill activate, and does a user-invoked one correctly stay silent. gbrain
ships a `routing-eval.jsonl` beside 41 of its 71 skills for exactly this. With seven of our nine
skills locked to explicit invocation, a routing failure is silent by construction — nothing fires, and
the person gets generic drafting instead of research-vault"
(`docs/product-landscape/2026-08-22-product-comparison-verified.md:1795-1802`). Fix: a
`routing-eval.jsonl`-style fixture per skill — phrasings a researcher would actually type, asserted
against the expected fire/silent outcome. Illustrative, drawn from this repo's own skill
descriptions rather than gbrain's actual schema (not read at that level of detail): `publish`'s
description already lists its own triggers — "Use when a person asks to publish, park, correct, or
withdraw a research-vault project" — so a fixture entry might assert `{"phrasing": "can we get this project out the door", "expect_fires": "publish"}` alongside a negative case
(`{"phrasing": "what's the citekey for this paper", "expect_fires": null}`) confirming a
model-invocable skill stays silent on an unrelated ask.

**No per-finding severity — every finding is equal weight within its check_id.** "Our severity is
per check id, not per finding: `CLOSING_BY_SURFACE` decides that `quote` can hold publish while
`screening-state` cannot, but two `quote` findings are equally weighty. Our `_FINDING_FIELDS` are
`id`, `check`, `target`, `result`, `date`, `actor`, `reason` — no severity among them. A trivial and
a serious instance of the same check are indistinguishable to the gate"
(`docs/product-landscape/...:1570-1576`) — medsci grades every finding major or minor and gates only
on majors, by contrast. Affects skill prose across `import-source`, `factcheck-draft`, `publish`, and
`project`, all of which describe findings uniformly. Fix: add a `severity` field to
`_FINDING_FIELDS`, populated by whichever check files the finding, and have the affected skills
report it alongside `result` rather than treating every finding as equally load-bearing —
mechanically, one new argument on the same verb §C's example above already shows:
`finding integrate CLAIM_LINK UNMATCHED "contradiction — ..." --vault PATH --severity major`, not a
new recording mechanism.

**UNREACHABLE has no mechanism that brings the check back.** `verify-citations` and `import-source`
both instruct: never describe an outage as a failure, never a verdict on the work. Correct as far as
it goes, but "saying an outage is not a failure only discharges half the obligation: something has to
bring the check back. Today an UNREACHABLE files a warn-tier finding that ages in the review inbox
alongside everything else, and nothing marks the note as *re-verify this when the registry is up*...
between imports, an outage is indistinguishable from a check that ran and passed unless a person
reads the queue" (`docs/product-landscape/...:1619-1626`) — research-hub's recheck marker, on a
transient-versus-permanent failure split, is named there as the direct precedent. Fix: a recheck flag
set on any UNREACHABLE outcome, cleared automatically the next time `verify` runs that check_id
successfully against the same target — "roughly a frontmatter field and a `verify` predicate," per
that same source, not a new subsystem.

**Before shipping any of A/B/C's fixes, pressure-test them.** `writing-skills` states its Iron Law as
binding on edits, not only new skills: "NO SKILL WITHOUT A FAILING TEST FIRST... This applies to NEW
skills AND EDITS to existing skills" (`skills/writing-skills/SKILL.md`) — baseline an agent without
the new prose or check, confirm it actually fails the way expected, then confirm the fix closes the
gap. None of this repo's nine skills show evidence of that baseline-then-verify cycle for their
current prose, and neither will A/B/C/D's own fixes unless it's applied to them before they ship.

## E. Reusable segments — patterns to adapt, not just cite

A/B/C/D name techniques and gaps; this section names specific passages, in specific already-read
`SKILL.md` files, close enough to this repo's own needs to adapt directly rather than reimplement
from a paper's description. `obra/superpowers` is MIT (Jesse Vincent, 2025) — reuse with
attribution is licensed, the same footing `find-sources` already vendors K-Dense's `paper-lookup`
skill on. None of the below is a license to paste verbatim: adapt into this repo's own voice and
conventions, the way `find-sources` itself does for its upstream.

- **`dispatching-parallel-agents/SKILL.md`** — its dispatch rule ("one agent per independent problem
  domain... issue in the same response = parallel," already quoted in §C) is short and general
  enough to adapt near-verbatim into `find-sources/SKILL.md` step 2 as the instruction for when a
  query spans more than one row of the routing table.
- **`subagent-driven-development/SKILL.md`** — the fix-loop *procedure* itself (5-round cap, rounds
  1-3 resume the same agent, rounds 4-5 escalate to a fresh agent on a stronger model, "adjudicate
  only at the cap," park-with-a-ruling instead of silent drop — already quoted in §C) is reusable
  wholesale for `import-source`'s debate-verdict loop and `project`'s gap-analysis loop once §C's
  second-subagent fix lands, rather than inventing new loop mechanics from scratch.
- **`requesting-code-review/SKILL.md`** — "precisely crafted context... never your session's
  history" (§B) plus its rationalization-table row against pasting session history in ports directly
  to whichever skill ends up dispatching the CoVe/debate subagent for §B or §C.
- **`verification-before-completion/SKILL.md`** and **`systematic-debugging/SKILL.md`** — reusable
  *format*, not content: an Iron Law statement, a rationalization table, a red-flags list (§A).
  `evidence-conventions/SKILL.md` already independently converged on half this shape via its own
  "Rationalizations, answered" table; `factcheck-draft` and `import-source` don't have one yet for
  their own discipline-type rules (e.g. never report UNREACHABLE as failed) and could adopt the same
  three-part shape.
- **`writing-for-agents/SKILL-MECHANICS.md`**'s router-skill pattern — "when user-invoked skills
  multiply past what you can remember, that piled-up cognitive load is cured by a router skill: one
  user-invoked skill that names the others and when to reach for each." This repo has seven
  user-invoked skills (`project`, `find-sources`, `import-source`, `publish`, `setup-vault`,
  `verify-citations`, `factcheck-draft`) — past the point this pattern exists for, and not currently
  used here.
- **`writing-for-agents/SKILL.md`**'s leading-word technique — collapsing a repeated multi-word
  phrase into one pretrained token the agent thinks with. This repo already does this well for
  "outage" (every UNREACHABLE result). "Four-state honesty" is the phrase that instead keeps getting
  restated four separate times (§A's fifth instance) — collapsing those four copies into
  `evidence-conventions` (§A fix 3) is also the natural moment to give the collapsed concept one
  settled name, closing both gaps in the same edit.

______________________________________________________________________

## Recommended terminology table

Covers A-D — the named, generalizable techniques. §E's segments are passages to adapt, not named
techniques in their own right, so they get no row.

| This repo's practice                                                                                                                                                            | Established name                                                                                                                                                                                                                                                                                                                      | Primary source                                                                                                                                                                                                                                                                                                                                                                                                                         |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A** — prose-only rule with a checkable predicate (`synthesis-conventions`'s 2+-source/2+-link rules; `find-sources`'s redaction fallback; the four-state table's four copies) | **Policy-as-code**, bounded to externally-checkable predicates — `writing-skills`'s "Match the Form to the Failure" names the complementary discipline-failure case where bulletproofed prose is correct instead; `writing-for-agents`'s "cache"/"single source of truth" doctrine reinforces the same fix from a token-economy angle | OPA docs (https://www.openpolicyagent.org/docs); Claude Skill authoring best practices (https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices); local vendor `skills/writing-skills`, `skills/verification-before-completion`, `skills/systematic-debugging` (path prefix `/home/eranr/.claude/plugins/cache/superpowers-dev/superpowers/6.2.0/`); `/home/eranr/.agents/skills/writing-for-agents/SKILL.md` |
| **B** — `factcheck-draft`'s single unverified LLM pass                                                                                                                          | **Factored verification** (already named in-repo) needing a **verify-the-verifier** second pass — already shipped as a forked-context subagent (pedrohcgs) and this session's own dispatching default (`requesting-code-review`)                                                                                                      | CoVe, arXiv 2309.11495; Self-Consistency, arXiv 2203.11171; SelfCheckGPT, arXiv 2303.08896; LLM-as-judge, arXiv 2306.05685; `docs/product-landscape/2026-08-22-product-comparison-verified.md:467-478`; local vendor `skills/requesting-code-review`                                                                                                                                                                                   |
| **C** — `import-source`/`project`/`find-sources` single-shot judgment                                                                                                           | **Adversarial/debate verification** and **orchestrator-workers/evaluator-optimizer** decomposition — `subagent-driven-development` supplies the round-cap/escalation/park mechanics; `dispatching-parallel-agents` is `find-sources`'s literal fix                                                                                    | Irving, Christiano, Amodei, arXiv 1805.00899; Du et al., arXiv 2305.14325; Anthropic, "How we built our multi-agent research system"; Anthropic, "Building Effective Agents"; `docs/product-landscape/...:339-368,487-494,1723-1726`; local vendor `skills/subagent-driven-development`, `skills/dispatching-parallel-agents`                                                                                                          |
| **D1** — no test checks a skill actually fires for realistic phrasing                                                                                                           | **Routing/firing evaluation**, distinct from schema/contract testing — no published or shipped-running tier found, shipped-and-comparable only                                                                                                                                                                                        | `docs/product-landscape/...:1795-1802` (gbrain's `routing-eval.jsonl`)                                                                                                                                                                                                                                                                                                                                                                 |
| **D2** — findings carry no severity, only a check_id-level closing decision                                                                                                     | **Per-finding severity grading**, distinct from per-check-id closing sets — no published or shipped-running tier found, shipped-and-comparable only                                                                                                                                                                                   | `docs/product-landscape/...:1570-1576` (medsci's major/minor gate)                                                                                                                                                                                                                                                                                                                                                                     |

## Dead ends / negative knowledge

- **RARR is a weaker fit than it first appears** for the `factcheck-draft` gap — its "research" step
  presumes open-ended evidence retrieval, but `factcheck-draft` deliberately checks a claim only
  against the one literature note it cites. RARR is better prior art for a future capability
  (checking beyond the cited source) than for closing today's single-pass gap.
- **FActScore names a metric, not a mechanism** — its atomic-fact decomposition matches this repo's
  existing `^claim-id` granularity almost exactly, so it supplies vocabulary (why per-claim is the
  right grain) rather than a new technique to adopt.
- **Mixture-of-Agents (Wang et al., 2024) was not independently WebFetched** — surfaced in search as
  the N-agent ensemble-voting variant, structurally covered for this note's purposes by
  self-consistency (§B) and the debate papers (§C); named only so the term is on record.
- **huytieu/COG-second-brain's "V-model verification lifecycle" is roster-tier, not a verified
  mechanism** — the source file marks this row ◐, its own defined meaning being "cloned and its tree
  listed, but no file opened... enough to confirm shape, licence and scale, not enough to describe a
  mechanism" (`docs/product-landscape/2026-08-22-product-comparison-verified.md:644-645`). Cited only
  for convergent naming against Self-Refine's failure mode (§B), not as a fourth confirmed
  implementation alongside Imbad0202, AgriciDaniel/claude-obsidian, and pedrohcgs.
