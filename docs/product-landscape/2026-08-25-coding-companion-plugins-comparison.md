# Coding-companion plugins: obra/superpowers vs mattpocock/skills

Comparison note, 2026-08-25. Question asked by the author: which of the two works better as the
coding companion for knowledge-harness, and what would switching from superpowers to mattpocock
cost — assuming all in-flight work done and one-time churn free, so the answer weighs steady state
only.

**Verdict (2026-08-25, superseding the same-day original below): the target architecture inverts —
mattpocock/skills becomes the base plugin, with three or four superpowers skills vendored as
adapted copies for heavy code batches.** The author's challenge to the original verdict survived
verification against the sources (ask-matt and code-review read in full; three of the original's
claims corrected below), and their strongest argument is this repo's own doctrine: mattpocock's
ticket discipline *eliminates* the lost-unresolved-concerns class that superpowers' ephemeral
workspaces created and this project patched with rules — every unit of work is born durable on a
tracker with blocking edges. Model alignment runs the same way: knowledge-harness is itself a
skill pack + `docs/agents/` config + tracker conventions (the `docs/agents/issue-tracker.md`
convention IS mattpocock's), with no session injection; and the coming workloads (PKM loop,
long-form writing) are ones where mattpocock's wayfinder/domain-modeling/codebase-design/
improve-codebase-architecture flows plus its beta writing suite (fragments/beats/shape,
explore/exploit) fit and superpowers has nothing. The superpowers skills that remain genuinely
unmatched — the SDD multi-round review loop, receiving-code-review, verification-before-completion,
finishing-a-development-branch — are text, vendorable via skills.sh into the existing
`~/.agents/skills` topology, invoked deliberately with no SessionStart injection.

**Corrections to the original (2026-08-25, same day):** (1) "no per-task machinery" was wrong —
ask-matt's main flow is to-spec → to-tickets → per-ticket `/implement` with `/clear` between,
each ticket driving `/tdd` internally and closing with `/code-review` (two parallel sub-agents)
before commit; per-task review exists, tracker-durable. What remains absent is the *loop*: the
findings→fix-dispatch→re-review-until-clean cycle and evidence-before-completion-claims
discipline. (2) The "public-tracker seam" cost was wrong as stated — a private repo's issues are
private, and the local tracker (`.scratch/<feature>/issues/`, one file per ticket, blockers-first)
is supported natively; tracker choice is per-repo configuration, not a plugin property. (3)
"code-review includes no verification" was too strong — its Spec axis verifies conformance against
the originating issue with quoted spec lines; what it lacks is fresh-evidence-before-claims and
the receiving-side skeptical discipline.

The original verdict and analysis follow, retained for the reasoning that still stands (the
deciding-delta section's catalogue of what the batch's review rounds caught remains the argument
for vendoring those specific superpowers skills rather than dropping them).

**Original verdict (2026-08-25, superseded):** superpowers stays the coding companion; the hybrid
already running (both installed, superpowers owning the dev-process lifecycle, mattpocock owning
tracker/domain hygiene) is the correct division of labor. The full-repo review strengthened the
incumbent: mattpocock's only per-task execution engine is beta and reviews once at the end, while
this repo's just-closed batch demonstrated that per-task review rounds and receiving-review
discipline are where its defects get caught. Two real superpowers frictions are named below with
mitigations, and one flip trigger is recorded.

## Evidence rule

Both repos inventoried at pinned states by fan-out agents reading primary source
(raw.githubusercontent.com + GitHub API + the local installs), 2026-08-25:

- `mattpocock/skills` @ `6654f6b` (HEAD of main, 2026-08-24) — full tree (`truncated: false`),
  every SKILL.md frontmatter read verbatim. 37 skills; 25 promoted in the Claude plugin.
- `obra/superpowers` — local install 6.2.0 read directly
  (`~/.claude/plugins/cache/superpowers-dev/superpowers/6.2.0/`), upstream HEAD `b36e082`
  (= v6.3.0 tag) diffed against it. 14 skills, unchanged across 6.2→6.3.
- Fit evidence: the post-q pre-slice batch (merged `d9b3acf..4b9f427`, 2026-08-25), executed
  end-to-end on superpowers SDD with mattpocock triage/domain-modeling running beside it.

## What each actually is

**superpowers (14 skills, MIT, release every 1–3 weeks)** is a process *engine*: brainstorming →
writing-plans → subagent-driven-development / executing-plans → requesting/receiving-code-review →
finishing-a-development-branch, plus TDD, systematic-debugging, using-git-worktrees,
verification-before-completion. Machinery: exactly one SessionStart hook injecting the
mandatory-invocation rules (`<EXTREMELY_IMPORTANT>`, the 1%-rule, Iron Laws) — no commands, no
agents, no MCP, no enforcing hooks; all gating is prompt-level. Subagent prompts and helper
scripts (sdd-workspace, task-brief, review-package) live inside skill dirs. Hard-coded paths:
`docs/superpowers/specs|plans`, `.superpowers/sdd/`, `.worktrees/`.

**mattpocock/skills (37 skills: 18 engineering, 7 productivity, 8 in-progress, 4 misc; MIT)** is a
skill pack that explicitly refuses to own the process layer (README: approaches like GSD/BMAD/
Spec-Kit "take away your control… small, easy to adapt, composable"). Tracker-centric: to-spec /
to-tickets (tracer-bullet tickets with blocking edges, frontier model) / triage / wayfinder publish
to the configured issue tracker. Has real TDD (seam-confirmed), a two-axis parallel code-review
(standards vs spec, requesting side only), hard-gated diagnosing-bugs, domain-modeling/CONTEXT/ADR,
grilling, wizard, handoff, research. No hooks, no commands; per-repo config via
`/setup-matt-pocock-skills`. Distribution: official-marketplace read-only plugin (sha pinned by
Anthropic) or skills.sh editable copies with a lockfile — pick one.

## The deciding delta

The stable mattpocock `implement` skill is six lines (use /tdd… use /code-review… commit) —
single session, no per-task machinery. The subagent-driven equivalent, `implement-spec`
(worktree-per-implementer, frontier concurrency), is in `in-progress/`, excluded from the plugin,
marked "can change or disappear without warning," and runs **one review at the end**, not
per-task rounds. Nothing in the catalog corresponds to receiving-code-review,
verification-before-completion, or finishing-a-development-branch.

Measured against the post-q batch: the disarmed-test catch, the stale-brief catch, the six-cell
empty-representations catch, the fail-open guard deletion, the None-idiom trap aversion — every
one arrived through per-task review rounds or receiving-review discipline (implementers verifying
the controller's claims before adopting them). For a trust-first repo whose doctrine is
records-tell-the-truth, superpowers' process side is the mirror of the product doctrine;
mattpocock's deliberately is not trying to be.

## Switching cost (churn excluded — permanent costs and gains)

Costs:

1. **Defect-escape rate.** Per-task two-stage review disappears (stable set) or becomes end-only
   (beta). Capability loss, not migration pain.
2. **Verification disciplines gone** — no verification-before-completion, no receiving-code-review;
   the process-side fail-closed posture becomes self-maintained prose.
3. **Beta dependency** — the only SDD-equivalent is explicitly disclaimed by its author.
4. **Public-tracker seam** — to-spec/to-tickets publish design content to the tracker; this repo's
   tracker is public GitHub, colliding with the vault↔repo privacy seam (§10's named open gap) for
   research-content workloads.

Gains (honest): the editable-copies update model (lockfile hashes; superpowers updates overwrite
silently — a hazard the author's global CLAUDE.md already documents), zero session-start injection
weight, and tracker-native planning that nests into the existing gh-issues/triage/wayfinder
investment. Every gain except the update model is available **without switching** — the packs
coexist, and already do here.

## Steady-state frictions of the incumbent, with mitigations

1. **SessionStart injection pressures every session toward skill invocation** — right for coding,
   wrong-shaped for the coming non-coding workloads (PKM loop, long-form). Already cost one
   settings surgery (grilling name-only override). Mitigation: per-skill `skillOverrides` in
   settings; revisit at the workload maps.
2. **Process governed by a fast upstream with silent overwrite on update.** v6.3.0 changed SDD
   behavior in this repo's direction — controller self-ruling on non-catastrophic plan conflicts,
   conflict scans ledgered, worktree removal no longer `--force`ing untracked files away —
   independently converging on what the post-q run built by hand. Mitigation: upgrades are
   deliberate reviewed events, not subscriptions; policy overlays live in settings/CLAUDE.md,
   never the vendored SKILL.md.

## Flip trigger (recorded, not predicted)

If the harness's center of gravity moves to non-coding workloads with only occasional small code
changes, the engine stops earning its injection weight and mattpocock-as-primary (superpowers
invoked per-project) becomes the right shape. That decision belongs to the workload maps (§10's
workload-pipelines entry), not to this note.

## Recommendations (superseded 2026-08-25 — see the superseding verdict at top)

Original recommendations, retained: keep the hybrid; deliberate 6.3.0 upgrade; adopt to-tickets/
code-review/diagnosing-bugs/ask-matt alongside; upstream filing stands.

## Revised target architecture (2026-08-25)

- **Base**: mattpocock/skills as the plugin layer — complete the install (the full promoted set,
  including ask-matt, code-review, tdd, diagnosing-bugs, implement, to-spec), via the skills.sh
  editable-copies path already in use (`npx skills add -g`), which matches the author's
  control preference; run `/setup-matt-pocock-skills` per repo (already done here — the
  `docs/agents/` layout is its output).
- **Vendored supplement**: subagent-driven-development, receiving-code-review,
  verification-before-completion, finishing-a-development-branch from obra/superpowers, adapted
  (cross-references to using-superpowers/writing-plans rewritten to stand alone), invoked
  deliberately for heavy code batches. Superpowers' SessionStart injection retires with the
  plugin — routing moves to AGENTS.md/CLAUDE.md, which this setup already relies on.
- **Ticket discipline as the concerns backbone**: units of work and their residuals are born on
  the tracker with blocking edges (native links, or one file per ticket locally); the
  write-time-destination rule for Concerns remains, with the tracker as its default destination.
- **Adaptation cost accepted**: vendored superpowers skills freeze at the vendored state and
  drift from upstream (no more free 6.3.0-style convergence); that is the control-over-currency
  trade the author has consistently chosen. The queued superpowers upstream filing stands.
- **Long-form writing leg**: wayfinder → grill-with-docs → to-spec/to-tickets, with
  domain-modeling underneath and the beta writing suite (fragments/beats/shape) evaluated when
  workload 3's map is drawn. Tracked as part of the §10 workload-pipelines entry.

## Final verdict — full-text pass (2026-08-25, supersedes both prior verdicts)

At the author's direction, all three skill corpora were loaded verbatim into one context — this
repo's 9 skills, superpowers' 14 plus the SDD dispatch prompts and reviewer templates,
mattpocock's promoted 25 — and the question rethought from primary text. Both prior verdicts were
partial views from partial instruments (agent inventories, then argument-and-response), and both
answered a false binary. **The correct architecture is layered, not based**: neither plugin
replaces the other because they govern different layers, and the repo already runs the correct
assignment.

What the full text shows that no inventory did:

1. **Genre alignment runs the other way at the doctrine layer.** This repo's skills are
   superpowers-genre texts — Iron Laws, rationalization tables answering excuses, four-state
   honesty tables, "never claim a check ran that did not." Evidence-conventions' Iron Law is
   verification-before-completion's Iron Law generalized into a product. Mattpocock skills are
   craft essays — compact, vocabulary-driven (seams, depth, frontier, fog), trusting the agent,
   with almost no anti-rationalization armor; their README disclaims wanting to own discipline.
   The mattpocock model-alignment claim (previous verdict) is true at the config/architecture
   layer — docs/agents/, tracker conventions, user-invoked skills, no injection, all already this
   repo's shape. Both alignments are real, at different layers.
2. **The execution-machine gap is wider in full text.** `/implement` has the implementing agent
   aggregate the review of its own work; SDD's controller never implements, its reviewer is told
   "do not trust the report — a stated rationale never downgrades a finding," its re-reviewer
   holds "attempted is not addressed," and its fix loop carries round caps, model escalation,
   adjudicate-only-at-the-cap, and ledger discipline. And mattpocock's code-review has no
   test-honesty axis at all — nothing reads tests adversarially ("tests that assert nothing" is
   an SDD reviewer rubric line), which is precisely the instrument that caught this batch's
   disarmed-test class (#22).
3. **The concerns-durability argument cuts differently than either verdict had it.** SDD's
   report contract is where Concerns come from; mattpocock's `implement` has no report contract —
   its machine loses fewer concerns partly by never birthing them. Tickets fix durability;
   removing the concern-generator is not a fix. The correct synthesis is the one already built:
   SDD's concern generation with write-time tracker destinations.
4. **Real mattpocock wins confirmed and sharpened by full text**: wayfinder is this repo's own
   provenance (the foundation map IS a wayfinder map) and the right instrument for the vault↔repo
   seam and workload maps; diagnosing-bugs' loop-first discipline ("no red-capable command, no
   hypothesis") is instrument-first debugging — arguably a better fit for this repo's
   measurement doctrine than systematic-debugging's four phases; to-tickets' expand–contract
   doctrine for wide refactors; writing-for-agents is the best available reference for editing
   this repo's own skills (its context-load principle IS the "every letter reduces compliance"
   rule) and should govern future skill edits here.
5. **The inverse hybrid's real cost surfaced**: SDD consumes writing-plans' plan-file format
   (task-brief extracts `### Task N`); to-tickets produces tickets. Vendoring SDD without
   writing-plans means adapting its substrate to tickets — natural (ticket body ≈ task brief,
   ticket comments ≈ ledger) but a fork with a real seam change, maintained forever, with
   6.3.0-class upstream convergence forfeited. Keeping the plugin and de-fanging the injection
   selectively in settings (`skillOverrides` name-only, the grilling precedent) gets nearly all
   of the inverse hybrid's benefit at none of the fork cost.

**Standing resolution**: keep both plugins. Layer governance — mattpocock owns repo config,
planning surfaces, domain language, and the tracker (it already does); superpowers' execution
core owns planned code changes on this repo (SDD + reviews + verification + finishing, injection
intact for dev sessions); this plugin is the doctrine both serve. Concrete adoptions: SDD
artifacts route to tracker destinations at write time (rule live); wayfinder for the seam and
workload maps (already planned); writing-for-agents as the reference for skill edits here;
evaluate diagnosing-bugs beside systematic-debugging at next real debugging need; revisit the
injection's session-start weight only when the PKM/writing workload maps make it a measured
problem, via settings, not plugin removal. The upstream filing and deliberate 6.3.0 upgrade
stand.

## Validation — recommendations tested against the session record (2026-08-25)

At the author's direction, each recommendation was replayed against the controller session's own
event history (the post-q batch and its surrounding work). Seven for seven supported; two blind
spots found.

1. **Layered governance**: the session ran the layers without collision — SDD executed the batch
   (21 rulings through its review machinery) while the mattpocock layer carried triage (#16), the
   ADR bar (0004's scope correction came from domain-modeling's three-test discipline), and the
   tracker (#18–#25). The one recorded layer-fight (grilling vs brainstorming) was settled in
   settings — the prescribed mechanism.
2. **Write-time destinations + SDD generation, both halves**: the disposition sweep found 12
   undisposed concerns across 31 sections; after the rule landed mid-batch, destinations were
   named at write time and 19b's residue became #25 with corrected framing. Counterfactual: 17b's
   concerns 1–4 (now #19/#20/#21 + spec §10.2) exist only because SDD's report contract demanded
   they be written — `implement` has no report contract, so under it they are never born.
3. **Wayfinder**: the author's workload-scoping session instinctively produced wayfinder's exact
   artifacts before anyone named it — banked decisions, a documented not-yet-specified gap,
   deliberate stop-short-of-design, and the sizing call "more than a single /wayfinder map."
4. **writing-for-agents**: the controller's Task-reports rule needed three revisions, and each
   defect is a named failure mode in that skill — the `.git/info/exclude` misclaim is its
   environment-as-cache warning; the skill-override was its single-source-of-truth violation; the
   pathspec-exception trim was its pruning/no-op test. Two of three revisions vanish under its
   governance.
5. **diagnosing-bugs**: the run's most expensive error class (instrument scope — the `.pop()`
   measurement missing `{"date-parts": []}`) maps directly onto its Phase-1 completion criterion:
   a red-capable loop asserting the exact symptom forces enumerating the representations until
   the common case goes red. systematic-debugging has no equivalent instrument criterion.
6. **Injection deferred to measurement**: consistent — implementer discipline rode the injection;
   no PKM session exists yet to measure the cost side.
7. **6.3.0 + upstream filing**: the session hand-built controller self-ruling (ratified with four
   named conditions), conflict-scan-in-ledger, and suffered the destructive-cleanup hazard —
   6.3.0 codifies the first two and softens the third; the filing stays motivated because
   workspace deletion at Finish remains ungated upstream.

Blind spots the test exposed, owned by no recommendation and no skill in any of the three sets:
(a) **the controller seat is ungoverned** — cross-session rulings, relay protocol, permission
hygiene, ratification conditions, and ask-vs-assume were improvised live and worked, but their
lessons live only in the batch retrospective and message history; SDD describes a controller
inside one plan, not the orchestration layer above it. (b) **Ruling latency under tracker
mediation is untested** — the session's mid-flight catches depended on a direct dialog channel;
tickets-as-backbone routes rulings through issue comments, and no event tests that round-trip
against a blocked implementer.
