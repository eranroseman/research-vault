# Ask-matt / setup-matt-pocock-skills / using-superpowers / superpowers-hooks investigation (issue #85)

Research note, 2026-08-28. Answers the three concrete-fact requests blocking #72, #61, #62, as
scoped by #85. Method: primary-source reads only — full `SKILL.md` files (not excerpts), the
superpowers hook script and its config, byte/line measurement of the actual injected payload.

**Provenance pins** (verdicts-name-their-instrument convention, per
`docs/product-landscape/2026-08-25-coding-companion-plugins-comparison.md`):

- `mattpocock/skills` fresh clone at `/tmp/mp-skills-verify`, commit `6654f6b60cd9d5be8b54c6fafe44346dabeb3b76`
  (2026-08-24T15:19:57+01:00) — the **same SHA** the 2026-08-25 comparison note and #72's
  2026-08-28 source-verification pass both used. No drift between instruments.
- `superpowers` 6.2.0, local plugin cache at
  `~/.claude/plugins/cache/superpowers-dev/superpowers/6.2.0/`.

## Step 0 — what the four prior docs already said (read first, to avoid duplicating)

Checked all four docs named in #85 for: the grill-with-docs/grilling delta, setup-matt-pocock-skills'
mechanism, and an "injection-weight problem" with superpowers' SessionStart hook.

- **grill-with-docs vs grilling**: not resolved in any of the four. `dev-harness-analysis.md:23`
  lists `grill-with-docs` alongside `grilling` in the "Elicitation" layer with no delta stated.
  `skill-inventory-gap-analysis.md` doesn't mention either name. The comparison doc's own §"Why
  not the inverse hybrid" and elsewhere don't touch grill-with-docs. This delta was genuinely
  unresolved before this note — consistent with #72 filing it as a formal blocker.

- **setup-matt-pocock-skills mechanism**: named as a pattern donor in three places but never
  described in mechanism detail:

  - `dev-harness-analysis.md:47`: "**Per-project scaffolding** (setup-matt-pocock-skills) — a
    one-time skill that writes the config other skills assume (tracker, labels, doc layout)."
  - `dev-harness-analysis.md:107`: "**scriptorium-setup** (from setup-matt-pocock-skills):
    one-time per-vault scaffolder: where sources live, citation style, inbox location,
    glossary/ruling-book layout, publish targets."
  - `skill-inventory-gap-analysis.md:186`: names it as the "pattern donor" for `vault-setup`,
    verdict "Covered", no further detail.
  - `comparison.md:53`: "per-repo via `/setup-matt-pocock-skills` (already run here; the
    `docs/agents/` layout is its output)" — confirms this exact repo's `docs/agents/` came from
    running it, but doesn't describe *how* it ran.
    None of the three give the interactive-wizard-shape detail #62 needs — that's new here (§2).

- **Superpowers SessionStart hook / "injection-weight problem"**: the *mechanism* is already
  documented, verbatim, in `plugin-packaging-mechanics.md:243-249` (§3.3, "What superpowers does
  with its hook"):

  > "`hooks/session-start` reads `skills/using-superpowers/SKILL.md` **in full** and injects it
  > wrapped in `<EXTREMELY_IMPORTANT>You have superpowers...` as SessionStart additionalContext.
  > So the brainstorming-first mandate is not merely a catalog description — it is standing
  > context in every session (matcher: startup/clear/compact)."

  A **behavioral-pressure** friction is also already documented, verbatim, in
  `comparison.md:130`:

  > "**SessionStart injection pressures every session toward skill invocation** — right for
  > coding, wrong-shaped for the coming non-coding workloads."

  Neither of these is phrased as "injection weight," and **neither gives a size measurement** —
  no byte count, line count, or token estimate for the payload anywhere in the four docs, or
  anywhere in `docs/` outside the raw unprocessed transcript export
  (`docs/research/raw/research-vault-transcripts/`, verified by grep, which is private-backup
  raw material, not a design doc). The exact string "injection weight" / "injection-weight"
  appears nowhere in any design doc. **The size characterization in §3 below is new
  information** — see the explicit statement at the end of §3.

Directory convention check: `docs/research/prior-art/` mixes plain-named files
(`plugin-packaging-mechanics.md`, `skill-inventory-gap-analysis.md`) with date-prefixed files from
recent research arcs (`2026-08-25-controller-orchestration-layer-prior-art.md`,
`2026-08-26-speckit-superpowers-bridge.md`). This note follows the date-prefixed pattern, matching
the most recent siblings in the same investigation thread. No filename collision (`git status`
confirmed after write, see end of note).

______________________________________________________________________

## Section 1 — ask-matt: grill-with-docs vs grilling (the load-bearing delta)

Source: `/tmp/mp-skills-verify/skills/engineering/ask-matt/SKILL.md`,
`/tmp/mp-skills-verify/skills/engineering/grill-with-docs/SKILL.md`,
`/tmp/mp-skills-verify/skills/productivity/grilling/SKILL.md` — all read in full.

### The headline finding: grill-with-docs is not a separate interview mechanism

`grill-with-docs/SKILL.md` in its **entirety** (6 lines including frontmatter):

```
---
name: grill-with-docs
description: A relentless interview to sharpen a plan or design, which also creates docs (ADR's and glossary) as we go.
disable-model-invocation: true
---

Call the Skill tool twice, for "grilling" and "domain-modeling".
```

(`/tmp/mp-skills-verify/skills/engineering/grill-with-docs/SKILL.md:7` — the entire body is that
one sentence.)

So `grill-with-docs` has **no interview logic of its own**. It is a two-call wrapper: it invokes
`grilling` (the interview primitive) and `domain-modeling` (the glossary/ADR discipline) together.
"Doc-grounded front door" describes the *bundling*, not a distinct interrogation mechanism —
the interview Claude runs under `grill-with-docs` is byte-for-byte the same `grilling` skill run
under `grill-me` or invoked bare.

### The exact routing text (ask-matt/SKILL.md)

`ask-matt/SKILL.md:17` (main flow, step 1):

> "**`/grill-with-docs`** sharpens the idea by interview. Start here whenever you are **working in
> a working directory**: it's stateful, retaining what it learns in `CONTEXT.md` and ADRs. (No
> working directory? Use `/grill-me` instead, covered under Standalone. Both run the same
> `/grilling` primitive; `grill-with-docs` is the one that leaves a paper trail, which makes it the
> better of the two whenever a repo is there to leave it in.)"

`ask-matt/SKILL.md:77` (Standalone section, on `grill-me`):

> "**`/grill-me`**: the same relentless interview as `/grill-with-docs`, but **stateless**: it
> saves nothing locally and builds no `CONTEXT.md`. Reach for it when you are **not working in a
> working directory** (sharpening a plan, a design, a piece of writing, anything with no repo
> under it). If you are in a working directory, use `/grill-with-docs` instead: it runs the same
> interview and leaves a paper trail, so it is strictly the better one."

`ask-matt/SKILL.md:78` (Standalone section, on `grilling` itself):

> "**`/grilling`** is the interview primitive itself: rounds, the frontier, facts are the agent's
> job and decisions are yours. `/grill-me` and `/grill-with-docs` are the two named ways in, and
> `/triage`, `/wayfinder` and `/improve-codebase-architecture` all run it internally. Reach for it
> directly only when you want the interview with no wrapper around it."

### The triad, precisely

- **`grilling`** (`/tmp/mp-skills-verify/skills/productivity/grilling/SKILL.md`) — the primitive:
  frontier-in-rounds interrogation ("Work the tree in **rounds**... Ask the whole frontier in one
  round... The session is done when the frontier is empty"). Description: "Grill the user
  relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their
  thinking, or uses any 'grill' trigger phrases." **No `disable-model-invocation` frontmatter** —
  this skill is model-invocable.
- **`grill-me`** — stateless wrapper (not read in full for this note; ask-matt's description at
  `ask-matt/SKILL.md:77` is the primary characterization used here). Saves nothing, builds no
  `CONTEXT.md`.
- **`grill-with-docs`** — stateful wrapper, `disable-model-invocation: true`
  (`grill-with-docs/SKILL.md:4`). Calls `grilling` + `domain-modeling` together, so the interview's
  output lands in `CONTEXT.md`/ADRs as it happens.

**Frontmatter asymmetry worth recording**: `grilling` is model-invocable (no invocation
restriction); both `grill-with-docs` and `ask-matt` itself carry `disable-model-invocation: true`
(`grill-with-docs/SKILL.md:4`, `ask-matt/SKILL.md:4`) — user-typed only. This is a decision input
for #72's front-door design, not just a naming detail: the primitive can fire on trigger phrases,
the doc-grounded wrapper cannot.

### Precondition named by ask-matt itself

`ask-matt/SKILL.md:90`: "**`/setup-matt-pocock-skills`**: run before your first engineering flow
to configure the issue tracker, triage labels, and doc layout the other skills assume."

______________________________________________________________________

## Section 2 — setup-matt-pocock-skills: the mechanism

Source: `/tmp/mp-skills-verify/skills/engineering/setup-matt-pocock-skills/SKILL.md`, read in full
(117 lines).

### What it sets up

- `docs/agents/issue-tracker.md` (always) — from one of three seed templates shipped in the
  skill's own folder (`issue-tracker-github.md`, `issue-tracker-gitlab.md`,
  `issue-tracker-local.md`), or written from scratch for "Other" trackers
  (`setup-matt-pocock-skills/SKILL.md:104-112`).
- `docs/agents/triage-labels.md` — **only if the `triage` skill is installed**
  (`SKILL.md:51,102,109`).
- `docs/agents/domain.md` — always, from `domain.md` seed template (`SKILL.md:110`).
- A `## Agent skills` block added to **whichever of `CLAUDE.md`/`AGENTS.md` already exists**
  (`SKILL.md:76-80`): "If `CLAUDE.md` exists, edit it. Else if `AGENTS.md` exists, edit it. If
  neither exists, ask the user which one to create; don't pick for them. Never create `AGENTS.md`
  when `CLAUDE.md` already exists (or vice versa); always edit the one that's already there." If
  the block already exists, it's **updated in place, not duplicated** (`SKILL.md:82`).
- No Cursor/other-harness-specific files are mentioned anywhere in the skill — it targets
  Claude-family agent-instruction files (`CLAUDE.md`/`AGENTS.md`/`GEMINI.md` are not enumerated
  beyond the CLAUDE.md/AGENTS.md pick logic) plus the `docs/agents/` directory it owns.

**Corroboration found in this very repo**: this repo's `AGENTS.md` already carries a `## Agent skills` block with exactly the three sub-sections (`### Issue tracker`, `### Triage labels`,
`### Domain docs`) in the exact wording/order the template specifies
(`setup-matt-pocock-skills/SKILL.md:86-100`), each pointing at `docs/agents/*.md` — matching
`comparison.md:53`'s claim that "the `docs/agents/` layout is its output." This is a live,
already-run instance of the mechanism, not just a documented pattern.

### How it does it — process, in order (SKILL.md:17-116)

1. **Explore** (`SKILL.md:19-30`) — read-only detection of current repo state before asking
   anything: `git remote -v`/`.git/config` (GitHub vs GitLab vs neither), existing
   `AGENTS.md`/`CLAUDE.md` and whether either already has an `## Agent skills` section,
   `CONTEXT.md`/`CONTEXT-MAP.md`, `docs/adr/`, `docs/agents/` (is this skill's prior output already
   there), `.scratch/` (local-tracker convention signal), whether the `triage` skill is installed,
   and monorepo signals (`pnpm-workspace.yaml`, `workspaces` field, populated `packages/*`).
2. **Present findings and ask** (`SKILL.md:32-61`) — "Summarise what's present and what's missing.
   Then take the sections in order. One section, one answer, then the next." Each section leads
   with a recommended default so "the user can accept it in a word"; sections are skipped
   entirely when their precondition isn't met (Section B/triage-labels skipped if `triage` isn't
   installed; Section C/multi-context skipped if no monorepo signals).
3. **Confirm and edit** (`SKILL.md:63-70`) — show the user a draft of the `## Agent skills` block
   and the contents of every `docs/agents/*.md` file about to be written; "Let them edit before
   writing."
4. **Write** (`SKILL.md:72-112`) — apply the file-pick rule above, update in place if the block
   exists, write the docs files from the seed templates bundled in the skill's own folder.
5. **Done** (`SKILL.md:114-116`) — tell the user setup is complete and which skills now read from
   these files; "re-running this skill is only necessary if they want to switch issue trackers or
   restart from scratch."

**Explicit framing** (`SKILL.md:15`): "This is a prompt-driven skill, not a deterministic script.
Explore, present what you found, confirm with the user, then write." — conversational and
human-in-the-loop at every step, not a fire-and-forget script, not a symlink or a copy operation.

### One-shot or repeatable?

Nominally one-time (frontmatter description: "Run once before first use of the other engineering
skills"), but explicitly **idempotent/safely re-runnable**: re-running only to switch trackers or
restart, and the write step updates the `## Agent skills` block in place rather than duplicating
it if run again. Not a single-use destructive install.

### What "a wizard modeled on this pattern" would concretely mean for #62

The reusable shape, extractable from the process above, is **detect → section-by-section
confirm-with-default → show-draft-before-write → templated materialization → idempotent re-run**,
not file copy/symlink and not a non-interactive script:

1. Read current state first, never assume it (Step 1) — for #62's harness-materialization wizard,
   that means probing what's already on the machine (existing `settings.json`, `CLAUDE.md`,
   `~/.codex` files, lockfile) before proposing anything.
2. Walk sections one at a time, each with a stated recommended default, skipping sections whose
   precondition doesn't apply (Step 2) — accept-in-a-word UX, not an exhaustive interrogation.
3. Show the exact draft of every file/block about to change and let the user edit before
   committing (Step 3) — a preview gate, not silent writes.
4. Materialize from templates shipped alongside the skill into a fixed, predictable destination
   convention (Step 4) — here `docs/agents/*.md`; for #62, the equivalent would be a fixed
   destination convention for each materialized artifact (settings.json keys, symlink targets,
   lockfile entries).
5. Support safe re-run as detect-and-repair, not a one-way irreversible install (Step 5) — a
   materialization wizard for #62 that can be re-run on drift, not just on first setup.

______________________________________________________________________

## Section 3 — superpowers SessionStart hook: what it injects, and the injection-weight question

Sources: `~/.claude/plugins/cache/superpowers-dev/superpowers/6.2.0/hooks/hooks.json`,
`.../hooks/session-start`, `.../skills/using-superpowers/SKILL.md` — all read in full.

### Registration (hooks.json, 17 lines, in full)

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start",
            "shell": "bash",
            "async": false
          }
        ]
      }
    ]
  }
}
```

Fires synchronously (`async: false`) on session startup, `/clear`, and `/compact`, dispatching to
`run-hook.cmd session-start` (a bash/Windows polyglot wrapper — see
`plugin-packaging-mechanics.md:218`), which runs the `session-start` script below.

### The wrapper script (`hooks/session-start`, 49 lines, 2274 bytes)

This is the mechanics layer, not the payload. It: locates the plugin root, `cat`s
`skills/using-superpowers/SKILL.md` **in full** into a variable
(`session-start:11`: `using_superpowers_content=$(cat "${PLUGIN_ROOT}/skills/using-superpowers/SKILL.md" ...)`),
JSON-escapes it (`session-start:16-24`), wraps it in one fixed template string
(`session-start:27`):

```
<EXTREMELY_IMPORTANT>\nYou have superpowers.\n\n**Below is the full content of your
'superpowers:using-superpowers' skill - your introduction to using skills. For all other
skills, use the 'Skill' tool:**\n\n${using_superpowers_escaped}\n</EXTREMELY_IMPORTANT>
```

and emits it as `SessionStart` `additionalContext`, branching only on which harness-specific JSON
shape to use (Cursor's `additional_context`, Claude Code's nested
`hookSpecificOutput.additionalContext`, or a generic top-level `additionalContext` for
Copilot CLI/others — `session-start:38-47`). **The injection is a single static file's bytes,
JSON-escaped and wrapped — not a dynamic assembly**: no globbing of other skills' frontmatter, no
generated skill list, nothing else concatenated.

### The actual payload (`skills/using-superpowers/SKILL.md`, 62 lines, 3063 bytes) — quoted in full

```markdown
---
name: using-superpowers
description: Use when starting any conversation - establishes how to find and use skills, requiring skill invocation before ANY response including clarifying questions
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, ignore this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If you think there is even a 1% chance a skill might apply to what you are doing, you ABSOLUTELY MUST invoke the skill.

IF A SKILL APPLIES TO YOUR TASK, YOU DO NOT HAVE A CHOICE. YOU MUST USE IT.

This is not negotiable. You cannot rationalize your way out of this.
</EXTREMELY-IMPORTANT>

## The Rule

**Invoke relevant or requested skills BEFORE any response or action** — including clarifying questions, exploring the codebase, or checking files. If it turns out wrong for the situation, you don't have to use it.

**Before entering plan mode:** if you haven't already brainstormed, invoke the brainstorming skill first.

Then announce "Using [skill] to [purpose]" and follow the skill exactly. If it has a checklist, create a todo per item.

## Skill Priority

When multiple skills apply, process skills come first — they set the approach, then implementation skills (frontend-design, etc.) carry it out. Brainstorming and systematic-debugging are Superpowers' most common process skills, but the rule holds for any of them.

- "Let's build X" → superpowers:brainstorming first, then implementation skills.
- "Fix this bug" → superpowers:systematic-debugging first, then domain skills.

## Red Flags

These thoughts mean STOP—you're rationalizing:

| Thought | Reality |
|---------|---------|
| "This is just a simple question" | Questions are tasks. Check for skills. |
| "I need more context first" | Skill check comes BEFORE clarifying questions. |
| "Let me explore the codebase first" | Skills tell you HOW to explore. Check first. |
| "I can check git/files quickly" | Files lack conversation context. Check for skills. |
| "Let me gather information first" | Skills tell you HOW to gather information. |
| "This doesn't need a formal skill" | If a skill exists, use it. |
| "I remember this skill" | Skills evolve. Read current version. |
| "This doesn't count as a task" | Action = task. Check for skills. |
| "The skill is overkill" | Simple things become complex. Use it. |
| "I'll just do this one thing first" | Check BEFORE doing anything. |
| "This feels productive" | Undisciplined action wastes time. Skills prevent this. |
| "I know what that means" | Knowing the concept ≠ using the skill. Invoke it. |

## Platform Adaptation

If your harness appears here, read its reference file for special instructions:

- Codex: `references/codex-tools.md`
- Pi: `references/pi-tools.md`
- Antigravity: `references/antigravity-tools.md`

## User Instructions

User instructions (CLAUDE.md, AGENTS.md, GEMINI.md, etc, direct requests) take precedence over skills, which in turn override default behavior. Only skip skill workflows or instructions when your human partner has explicitly told you to.
```

(`~/.claude/plugins/cache/superpowers-dev/superpowers/6.2.0/skills/using-superpowers/SKILL.md:1-63`.)

### Content categories injected

1. A subagent escape clause (ignore this skill if dispatched as a subagent for a specific task).
2. A mandatory-invocation imperative (the "1% rule" — "YOU DO NOT HAVE A CHOICE").
3. "The Rule" — invoke before any response, brainstorm before plan mode, announce usage.
4. "Skill Priority" — process skills before implementation skills, with two worked trigger→skill
   examples.
5. "Red Flags" — an 11-row rationalization/rebuttal table.
6. "Platform Adaptation" — pointers to three per-harness reference files (not themselves injected;
   read only if that harness applies).
7. "User Instructions" — the precedence clause (user CLAUDE.md/AGENTS.md/direct requests override
   skills) — the same clause `plugin-packaging-mechanics.md:322-325` already cites as the
   documented escape hatch for the grilling-vs-brainstorming collision.

### Size characterization

- Wrapper script: 49 lines / 2274 bytes (mechanics only — not injected itself).
- Injected payload source file: **62 lines / 3063 bytes**.
- Actual injected string ≈ payload bytes + the fixed wrapper text (~230–250 bytes of literal
  template + JSON envelope) ≈ **~3.3 KB total**, roughly 750–800 tokens by rough estimate (not
  measured with a tokenizer — an estimate, not a counted figure).
- This is well under the documented 10,000-character per-hook `additionalContext` cap noted in
  `plugin-packaging-mechanics.md:236-238`.
- The injection is a single static file, unconditionally injected in full on every
  startup/clear/compact — not conditionally assembled, not scaled by repo size or skill count.

### Cross-reference: was "injection-weight" already documented locally?

**Three distinct things, not one, and only the third is new:**

1. **The mechanism** (full-file injection wrapped in a fixed template) — **already documented**,
   quoted above from `plugin-packaging-mechanics.md:243-249` (§0).
2. **A behavioral-pressure friction** (biases every session toward skill invocation, "wrong-shaped
   for non-coding workloads") — **already documented**, quoted above from `comparison.md:130`
   (§0). This is almost certainly the friction #61's text means by "the injection-weight problem
   already flagged in the incumbent hook" — but note it is a *directional/behavioral* claim, not a
   *size* claim.
3. **The literal term "injection-weight" and any byte/line/token size measurement** — appear
   **nowhere** in any design doc in `docs/` (confirmed by grep across `docs/`, excluding the raw
   transcript export). **This is new information supplied by this note.**

The corrective worth stating plainly for #61: **the payload itself is small** (3063 bytes / 62
lines, ~3.3 KB wrapped, far under the 10,000-char hook cap) — it is not bloated by volume. If a
"weight" problem is real, it is a problem of *content and tone* (the unconditional "1% rule"
imperative plus the red-flags rationalization table pushing toward invocation in every session,
regardless of workload) rather than *bytes injected*. #61 should treat size and behavioral
pressure as two separate axes when deciding what a "lean router" for the companion drops or keeps.

______________________________________________________________________

## Section 4 — implications for #61, #62, #72

### #72 (front-door pipeline disposition)

- The "Not yet specified" gap — "the grill-with-docs-vs-plain-grilling delta" — is now answered:
  `grill-with-docs` has no bespoke interview logic; its entire body calls `grilling` +
  `domain-modeling` (`grill-with-docs/SKILL.md:7`). "Doc-grounded front door" means *bundling*
  grilling with domain-modeling's CONTEXT.md/ADR capture, not a distinct interrogation mechanism.
  "Kept deliberately distinct from grilling upstream" is **true at the wrapper/invocation-policy
  level, false at the interview-mechanism level** — the interview itself is identical.
- New decision input for the front door design: `grilling` is model-invocable (fires on trigger
  phrases, no `disable-model-invocation`), while `grill-with-docs` and `ask-matt` are both
  `disable-model-invocation: true` — user-typed only. Any front-door skill modeled on
  `grill-with-docs` inherits that same user-typed-only invocation posture unless deliberately
  changed.
- ask-matt's own routing rule is mechanical and quotable: working directory present →
  `grill-with-docs`; no working directory → `grill-me` (stateless). This is a ready-made rule for
  #72 to adopt or explicitly diverge from.

### #61 (SessionStart hook — lean router)

- Concrete facts on the reference hook: it injects one static file
  (`using-superpowers/SKILL.md`, 62 lines/3063 bytes) verbatim via a 49-line wrapper script, on
  `startup|clear|compact`, well under the 10,000-char hook cap.
- The "injection-weight problem" #61 cites as "already flagged" is the **behavioral-pressure**
  friction from `comparison.md:130`, not a size claim — no prior doc measured the payload's size.
  This note supplies that measurement for the first time.
- Actionable framing for the lean-router design: don't conflate "make it small" with "make it not
  pressure every session" — the reference hook is already small; its problem (if any) is the
  unconditional imperative tone plus the red-flags table, not byte count. A companion router that
  is equally small in bytes could still reproduce the same pressure problem if it copies that
  tone; conversely, dropping the tone doesn't by itself save meaningful bytes (there weren't many
  to save).

### #62 (setup/materialization mechanism)

- Full mechanism now on record: `setup-matt-pocock-skills` is a **prompt-driven, human-in-the-loop
  wizard skill**, not a script, not a copy/symlink operation. Shape: detect existing state →
  section-by-section confirm-with-recommended-default (skip inapplicable sections) → show a draft
  of every file/block before writing → materialize from bundled seed templates into a fixed
  destination convention → idempotent re-run (update in place, re-run only to switch config or
  restart).
- This is directly transferable to #62's "one-command harness-materialization wizard": detect
  current machine state (existing `settings.json`, `CLAUDE.md`, `~/.codex` files, lockfile) before
  proposing changes; walk each materialized concern as its own confirm-with-default section;
  preview every write; support safe re-run as drift-repair rather than one-shot install.
- This repo's own `AGENTS.md` `## Agent skills` block and `docs/agents/*.md` files are a live,
  verified instance of the mechanism already having run here — direct confirmation the documented
  process matches production behavior, not just the SKILL.md's stated intent.

______________________________________________________________________

## Section 5 — `superpowers:brainstorming` vs. `domain-modeling` and the proposed synthesis skill (2026-08-29 addendum, for #72)

Source: `~/.claude/plugins/cache/superpowers-dev/superpowers/6.2.0/skills/brainstorming/SKILL.md`
and its `scripts/`/companion files, read in full;
`/tmp/mp-skills-verify/skills/engineering/domain-modeling/SKILL.md`, read in full.

### `domain-modeling` vs. brainstorming: no content overlap

Grepped `brainstorming/SKILL.md` for every term the banked #72 synthesis-skill proposal wants a
new skill to own — "adr", "glossary", "context.md", "user stor[y/ies]", "out of scope", "seam",
"staleness"/"file path"/"snippet" — **zero matches for all of them**. Brainstorming never mentions
a glossary, never mentions ADRs, never cross-references code-vs-stated-behavior, never bans file
paths or snippets, produces no user stories, and has no dedicated Out-of-Scope section. Its own
design-doc checklist is "architecture, components, data flow, error handling, testing" — a
different, non-overlapping list. So as content, `domain-modeling`'s glossary/ADR discipline is a
pure addition on top of brainstorming, not a duplicate of anything brainstorming already does.

### But the proposed synthesis skill's *process shape* does collide with brainstorming

Brainstorming does not just supply content — it asserts **hard, exclusive ownership** of the
pre-implementation phase. Quoted verbatim:

> `<HARD-GATE>Do NOT invoke any implementation skill, write any code, scaffold any project, or take any implementation action until you have presented a design and the user has approved it. This applies to EVERY project regardless of perceived simplicity.</HARD-GATE>`

> "You MUST use this before any creative work - creating features, building components, adding
> functionality, or modifying behavior." (its own trigger description)

> "The terminal state is invoking writing-plans. Do NOT invoke frontend-design, mcp-builder, or any
> other implementation skill. The ONLY skill you invoke after brainstorming is writing-plans."

Brainstorming's own checklist already implements essentially the full shape the banked proposal
wants for a new synthesis skill: ask-questions-one-at-a-time → propose-2-3-approaches →
present-design-with-per-section-approval → write-design-doc-and-commit → a **spec self-review**
step (placeholders/contradictions/scope/ambiguity — near-identical in kind to an
adversarial-verification pass) → a **user review gate** on the written spec → invoke writing-plans.
That is the same lifecycle slot the banked proposal wants for its new synthesis skill
(dialogue → spec artifact → self-review → user-approval gate → handoff to writing-plans/SDD), minus
the specific glossary/ADR/user-story/Out-of-Scope/anti-staleness content and a separate
adversarial-verification step.

This is not just an internal detail — it collides directly with a standing global instruction
(`~/.claude/CLAUDE.md`): "Process — how work happens — is owned by the installed superpowers
skills (brainstorm → plan → TDD/SDD → review → finish...)." A new synthesis skill built as a
parallel front door that re-implements dialogue → spec → self-review → user-gate → writing-plans
would duplicate brainstorming's **process**, not just risk redundant content — unless it is
explicitly composed as a step inside/after brainstorming (e.g. grilling + domain-modeling invoked
during brainstorming's own "Explore project context," "Present design," or "Write design doc"
steps) rather than built to stand beside it as a competing top-level gate. The proposal's own
framing — grilling + domain-modeling as "shared invoked primitives" — is already compatible with
slotting into brainstorming's existing checklist rather than building a rival pipeline.

**Sharper question for #72, replacing "does synthesis duplicate brainstorming's content" (it
doesn't):** does the front door's proposed synthesis skill duplicate brainstorming's
**gate/terminal-state role** — and if the front door is meant to be genuinely distinct from
brainstorming's coding-workflow ownership (per the CLAUDE.md line "confusing brainstorming with
brainstorming and grilling is the failure this rule exists to prevent" — the friction is naming,
but the deeper issue is two skills both claiming the same "before you build, gate on approval"
slot), the design needs to say explicitly whether the new skill composes with brainstorming or
replaces it for the companion's own workflows.

### One more data point: brainstorming's weight, for #61's benefit

Beyond `SKILL.md` itself, brainstorming ships a substantial **optional** visual-companion
subsystem: a hand-rolled HTTP+WebSocket server (`scripts/server.cjs`, 723 lines, manual RFC 6455
framing, no `ws` dependency), a browser-side helper (167 lines), an HTML frame template (213
lines), start/stop lifecycle scripts (329 lines combined), a 298-line usage guide, and a 49-line
reviewer-prompt file — **~1,779 lines across 7 files**, larger by raw size than the SKILL.md body
itself. It's opt-in and offered "just-in-time" (never upfront, never invoked if no visual question
arises), but it means brainstorming's *total* footprint is an order of magnitude heavier than
grilling's simple, server-free interview loop. Relevant to #61's "lean router" framing: the weight
asymmetry between skills in this roster varies enormously, and grilling is toward the light end of
it, not the heavy end.
