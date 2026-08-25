# Coding-companion plugins: obra/superpowers vs mattpocock/skills

Comparison note, 2026-08-25. The author's question: which of the two works better as the coding
companion for knowledge-harness, and what would switching from superpowers to mattpocock cost —
assuming in-flight work done and one-time churn free, so only steady state counts.

**Verdict (2026-08-25, third pass, derived from full primary text; conditioned by the same-day
rethink audit): the question is a false binary — the correct architecture is layered, not based,
and the repo already runs the correct assignment — CONDITIONED on the bridge between the layers
being maintained as its own named piece.** Mattpocock owns repo config, planning surfaces, domain
language, and the tracker (it already does); superpowers' execution core owns planned code
changes (SDD + reviews + verification + finishing, injection intact for dev sessions); this
plugin is the doctrine both serve. Neither replaces the other because they govern different
layers. The clean-slate audit
([rethink audit](../../research/rethink-audits/2026-08-25-coding-companion-plugin-layering-rethink-audit.md))
stress-tested this verdict against field evidence and upheld it with the condition — see "The
bridge" below. Two earlier same-day verdicts were superseded — see Verdict history at the end.

## Evidence rule

Verdicts name their instrument (a convention this note's own arc argues for — its three verdicts
came from three instruments and only the third had the scope its claims needed):

- Repo inventories by fan-out agents at pinned states: `mattpocock/skills` @ `6654f6b` (full
  tree, every frontmatter verbatim; 37 skills, 25 promoted in the plugin), `obra/superpowers`
  local 6.2.0 + upstream `b36e082` (= v6.3.0; 14 skills, unchanged 6.2→6.3).
- Full-text pass: all three corpora loaded verbatim into one context — this repo's 9 skills,
  superpowers' 14 plus the SDD dispatch prompts and reviewer templates, mattpocock's promoted set,
  plus the beta `implement-spec` and writing suite.
- Fit evidence: the post-q pre-slice batch (merged `d9b3acf..4b9f427`), executed end-to-end on
  superpowers SDD with mattpocock triage/domain-modeling running beside it, and this controller
  session's event record.
- Adversarial pass: a clean-slate rethink audit (requires → prior-art → design → gap → migrate),
  its eight external citations independently verified — seven confirmed with verbatim quotes,
  one mismatch corrected (nocoders.com compares the packs but never argues against layering;
  that argument belongs to the zenn.dev piece alone), two provenance caveats recorded (obra's
  #1007 position was posted by an AI agent from his account at his direction; its "#163 played
  out the same way" is that comment's retroactive gloss).

## What each is

**superpowers (14 skills, MIT, release every 1–3 weeks)** is a process *engine*: brainstorming →
writing-plans → subagent-driven-development / executing-plans → requesting/receiving-code-review →
finishing-a-development-branch, plus TDD, systematic-debugging, using-git-worktrees,
verification-before-completion. Machinery: exactly one SessionStart hook injecting the
mandatory-invocation rules (the 1%-rule, Iron Laws) — no commands, agents, MCP, or enforcing
hooks; all gating is prompt-level. Hard-coded paths: `docs/superpowers/specs|plans`,
`.superpowers/sdd/`, `.worktrees/`.

**mattpocock/skills (37 skills; MIT)** is a skill pack that explicitly refuses to own the process
layer ("small, easy to adapt, composable"). Tracker-centric: to-spec / to-tickets (tracer-bullet
tickets with blocking edges, frontier model) / triage / wayfinder publish to the configured
tracker — GitHub, GitLab, or local one-file-per-ticket, per-repo via `/setup-matt-pocock-skills`
(already run here; the `docs/agents/` layout is its output). Has seam-confirmed TDD, a two-axis
parallel code-review (standards vs spec, requesting side only), hard-gated diagnosing-bugs,
domain-modeling/CONTEXT/ADR, grilling, wizard, handoff, research. No hooks, no injection.
Distribution: read-only official-marketplace plugin or skills.sh editable copies with a lockfile.

## The deciding delta: the execution machine

Mattpocock's per-task machinery is real but thin. The main flow (ask-matt) runs to-spec →
to-tickets → per-ticket `/implement` with `/clear` between, each ticket driving `/tdd` and
closing with `/code-review` before commit — per-task review exists, tracker-durable. But
`/implement` is six lines and has the implementing agent aggregate the review of its own work;
the beta `implement-spec` (36 lines, in-progress, "can change or disappear") adds frontier
concurrency and worktree-per-implementer with **one** review at the end — no report contract, no
fix-round caps or escalation, no test-evidence discipline, no ledger.

SDD's machine, by contrast: the controller never implements; the reviewer is instructed "do not
trust the report — a stated rationale never downgrades a finding"; the re-reviewer holds
"attempted is not addressed"; the fix loop carries round caps, model escalation,
adjudicate-only-at-the-cap, and ledger discipline. Nothing in mattpocock's catalog corresponds to
receiving-code-review, verification-before-completion, or finishing-a-development-branch, and its
code-review has no test-honesty axis — nothing reads tests adversarially ("tests that assert
nothing" is an SDD rubric line).

Measured against the post-q batch: the disarmed-test catch (#22's class), the stale-brief catch,
the six-cell empties, the fail-open guard deletion, the None-idiom aversion — every one arrived
through per-task review rounds or receiving-review discipline. For a trust-first repo, that
machine is the process-side mirror of records-tell-the-truth.

Two findings settle the layer question:

- **Genre**: this repo's skills are superpowers-genre texts — Iron Laws, rationalization tables,
  four-state honesty, "never claim a check ran that did not" (evidence-conventions' Iron Law is
  verification-before-completion's, generalized into a product). Mattpocock skills are craft
  essays — compact, vocabulary-driven, trusting the agent, by stated design. Mattpocock's
  alignment with this repo is real at the config/architecture layer (docs/agents/, tracker,
  user-invoked skills, no injection); superpowers' is real at the doctrine layer. Different
  layers, both true.
- **Concerns durability**: SDD's report contract is where Concerns come from; `implement` has no
  report contract, so its machine loses fewer concerns partly by never birthing them (the post-q
  evidence: 17b's concerns 1–4 — now #19/#20/#21 + spec §10.2 — exist only because the contract
  demanded they be written). Tickets fix durability; removing the concern-generator is not a fix.
  The synthesis already built here is correct: SDD generation + write-time tracker destinations.

## What mattpocock wins, adopted or adoptable

- **wayfinder** — this repo's own provenance (the foundation map IS a wayfinder map); the right
  instrument for the vault↔repo seam and workload maps.
- **diagnosing-bugs** — loop-first ("no red-capable command, no hypothesis") is instrument-first
  debugging, arguably a better fit for this repo's measurement doctrine than
  systematic-debugging's four phases; evaluate at the next real debugging need.
- **writing-for-agents** — the best available reference for editing this repo's own skills; its
  context-load principle is the "every letter reduces compliance" rule written out. Governs
  future skill edits here.
- **to-tickets** — expand–contract doctrine for wide refactors; tracker-native planning nesting
  into the existing gh-issues/triage investment.
- **The beta writing suite (fragments/beats/shape)** — a real explore/exploit discipline, not a
  curiosity: fragments is diary-mining via grilling and maps onto the PKM capture-streams
  decision; beats/shape track a **grounding set** and offer only reachable next moves — the
  ticket-graph frontier model applied to prose dependencies, one mental model
  (blocked-until-grounded) across code and writing. Serious candidates for workload 3's map;
  beta status is the only caveat (vendor a snapshot if adopted).
- Two ideas from `implement-spec` worth stealing without adopting it: the exploration-subagent
  pre-pass (the institutionalized form of the pre-check practice that produced the batch's two
  zero-fix-round tasks) and context-pointer communication for dispatches.

## Why not the inverse hybrid (mattpocock base + vendored superpowers skills)

Considered and rejected in the second pass's favor, then unwound by full text: SDD consumes
writing-plans' plan-file format (task-brief extracts `### Task N`); to-tickets produces tickets.
Vendoring SDD without writing-plans means adapting its substrate — natural (ticket ≈ brief,
comments ≈ ledger) but a fork maintained forever, with 6.3.0-class upstream convergence
forfeited. De-fanging the injection selectively in settings (`skillOverrides` name-only, the
grilling precedent) gets nearly all the benefit at none of the fork cost.

## Frictions of the incumbent, with mitigations

1. **SessionStart injection pressures every session toward skill invocation** — right for coding,
   wrong-shaped for the coming non-coding workloads. Mitigation: per-skill `skillOverrides`;
   revisit only when the PKM/writing maps make it a measured problem — via settings, never plugin
   removal. Flip trigger, recorded not predicted: if the harness's center of gravity moves to
   non-coding work, mattpocock-as-primary becomes the right shape; that decision belongs to the
   workload maps.
2. **Process governed by a fast upstream with silent overwrite on update.** Mitigation: upgrades
   are deliberate reviewed events; policy overlays live in settings/CLAUDE.md, never the vendored
   SKILL.md. The 6.2.0→6.3.0 upgrade is recommended — it codifies three practices the post-q run
   hand-built (controller self-ruling, conflict-scan ledgers, non-destructive worktree cleanup) —
   with one premise re-check in the ritual: the user-level Task-reports rule cites the SDD Finish
   step (confirmed at today's HEAD: Finish still deletes the workspace, so the queued upstream
   filing — deletion gated on concern dispositions — stays motivated).

## The bridge — the layered verdict's condition (rethink audit, 2026-08-25)

The audit's central contribution: the architecture has **four pieces, not three** — the
execution-discipline module (adapter: superpowers), the repo-policy module (adapter: mattpocock),
the doctrine module (this repo's invariants, read unconditionally, not an adapter), and **the
bridge**: this repo's own responsibility for reconciling the two adapters' trigger surfaces at
their collision points. Today the bridge is one settings override (grilling ↔ brainstorming).

Field evidence says unbridged layering fails in the wild, and the citations were verified:

- A mattpocock user (discussion #257) had a `ready-for-agent`, fully-specified task; superpowers'
  mandatory brainstorming fired anyway and started a design-doc process — he disabled superpowers
  over exactly this. Verbatim confirmed.
- The zenn.dev comparison argues "philosophical conflict… you should choose one or the other"
  (the 1%-rule false-positives against mattpocock skills). Confirmed verbatim. (nocoders.com,
  previously lumped with it, makes no such argument — corrected.)
- Three downstream tools that faced both packs all reconciled by mutual-exclusion detection,
  fusion into one canon, or pick-one-with-selective-retention — none ran raw side-by-side.
- Superpowers' side (#1007, provenance caveat above): "the tools compose fine, and the bridging
  logic lives in the consuming tool rather than upstream." This repo IS the consuming tool.

Every cited failure is an *unbridged* raw install; this repo's post-q batch ran both layers live
with zero collision — but partly because the batch never entered through a ticket. The one
unmitigated collision here today is the field-reported one: **a fully-specified tracker ticket
meeting mandatory brainstorming.** The audit checked `skillOverrides`' schema (static enum, no
conditional form — a settings mechanism cannot express "skip brainstorming when the ticket is the
spec"), so the fix is honestly a rule, in `docs/agents/issue-tracker.md`: *a `ready-for-agent`
issue IS the spec; execution enters at plan/SDD, brainstorming is not re-invoked.* Plan W's
tracker-mediation pilot exercises this path.

### Recommendations from the audit (recorded 2026-08-25, not yet landed)

1. **The bridge rule** — one line in `docs/agents/issue-tracker.md`: a `ready-for-agent` issue IS
   the spec; execution enters at plan/SDD; brainstorming is not re-invoked. Closes the one
   collision this setup is exposed to today (audit gap F, the load-bearing one).
2. **The scope statement** — one line in AGENTS.md: the layering decision's mechanism
   (`skillOverrides`/`enabledPlugins`) is deliberately user-global (`~/.claude/settings.json`; no
   project settings file exists), stated so the per-repo language and the global mechanism don't
   sit in unstated tension (audit gap C).
3. **The mattpocock update ritual** — one line in `docs/agents/`: on `npx skills update`, review
   the lockfile hash-diff before accepting, mirroring superpowers' reviewed-upgrade ritual (audit
   gap E).
4. **ADR 0005 — the layering decision itself** — mattpocock owns config/planning/tracker/domain
   language, superpowers' execution core owns planned code changes, this repo's doctrine binds
   both, the bridge is this repo's responsibility. Passes the three-test bar in the controller's
   reading (hard to reverse, surprising without context, real trade-off); recorded here so future
   domain-modeling passes can flag conflicts against it once accepted — the author's word decides
   (audit gap B).

Remaining dispositions: the four-state dedup stays the post-slice candidate; the audit's
controller-seat gap was stale — the note it asks for already exists
(research/validation-slice/2026-08-25-controller-protocol-material.md).

## Validation — recommendations tested against the session record

Each recommendation replayed against this controller session's event history. Seven for seven
supported; two blind spots found.

1. **Layered governance**: the session ran the layers without collision — SDD executed the batch
   (21 rulings through its review machinery) while the mattpocock layer carried triage (#16), the
   ADR bar (0004's scope correction), and the tracker (#18–#25). The one recorded layer-fight
   (grilling vs brainstorming) was settled in settings — the prescribed mechanism.
2. **Write-time destinations + SDD generation**: the disposition sweep found 12 undisposed
   concerns across 31 sections; after the rule landed mid-batch, destinations were named at write
   time and 19b's residue became #25 with corrected framing. The counterfactual is the
   concerns-durability finding above.
3. **wayfinder**: the author's workload-scoping session instinctively produced its exact
   artifacts before anyone named it — banked decisions, a not-yet-specified gap, deliberate
   stop-short-of-design, "more than a single /wayfinder map."
4. **writing-for-agents**: the controller's Task-reports rule needed three revisions; each defect
   is a named failure mode in that skill (environment-as-cache; single-source-of-truth; the
   pruning/no-op test). Two of three revisions vanish under its governance.
5. **diagnosing-bugs**: the run's most expensive error class (instrument scope — the `.pop()`
   measurement missing `{"date-parts": []}`) maps onto its Phase-1 red-capable-loop criterion;
   systematic-debugging has no equivalent.
6. **Injection deferred to measurement**: consistent — implementer discipline rode the injection;
   no PKM session exists yet to measure the cost side.
7. **6.3.0 + upstream filing**: three hand-built convergences and one suffered hazard, as in the
   frictions section.

Blind spots, owned by no recommendation and no skill in any of the three sets: (a) **the
controller seat is ungoverned** — cross-session rulings, relay protocol, permission hygiene,
ratification conditions, ask-vs-assume were improvised live and worked, but their lessons live
only in the batch retrospective and message history; SDD describes a controller inside one plan,
not the orchestration layer above it. (b) **Ruling latency under tracker mediation is untested**
— the session's mid-flight catches depended on a direct dialog channel; a one-ruling pilot is
registered in Plan W.

## Further insights

1. **The empty niche is this plugin's.** Neither catalog has anything for evidence and trust —
   verification records, four-state honesty, admission boundaries, deprecate-never-delete. The
   doctrine layer of this repo's nine skills is portable to any knowledge work with citable
   sources; if harness-as-paper materializes, harness-as-published-skill-pack is its sibling with
   no competitor in either catalog.
2. **A sharper criterion for the process-belongs-to-user split, observed live**: the session's
   cross-session verification refusals were receiving-code-review discipline running WITHOUT
   invocation, because the doctrine lives in artifacts every session reads unconditionally.
   Universally-binding discipline goes where every session reads it (AGENTS.md / CLAUDE.md);
   role-specific process goes in invocable skills. That is why the trust culture propagated to
   five peer sessions unprompted while the SDD process needed a dispatch each time.
3. **This repo's own pack violates the doc-design principle it just adopted**: the four-state
   honesty table appears in four skills, each a local restatement — duplication by
   writing-for-agents' single-source-of-truth rule, and the exact "restatement that drifts from
   the guard" failure project-flow warns about. Post-slice audit candidate: one canonical
   four-state reference, per-skill deltas only (or a recorded decision that per-surface semantics
   justify the copies).
4. **The controller-seat gap has a decaying-evidence fix** — executed same day: the protocol is
   banked at research/validation-slice/2026-08-25-controller-protocol-material.md (delegation
   conditions, word hygiene, dispute adjudication, the seat's own error ledger), material for
   whenever the orchestration layer gets a real home.

## Verdict history

Three same-day passes, each named by its instrument; the corrections are the record of what each
instrument missed.

1. **Installed-subsets pass** (agent inventories of the local installs): "superpowers stays; keep
   the hybrid." Wrong in three particulars the second pass corrected: mattpocock DOES have
   per-task machinery (per-ticket implement + code-review, tracker-durable — what it lacks is the
   fix loop and evidence-before-claims); tracker privacy is per-repo configuration, not a plugin
   cost (private repo → private issues; local tracker supported); code-review's Spec axis IS
   conformance verification (what it lacks is fresh-evidence and receiving-side discipline).
2. **Argument-response pass** (author's challenge, sources spot-read): "invert — mattpocock base,
   vendor four superpowers skills." Its lasting contributions: the ticket-discipline insight and
   the model-alignment observation, both absorbed into the final verdict at their correct layer.
   Its error: overweighting the architecture layer because the challenge was fresh, and pricing
   the vendoring fork at zero.
3. **Full-text pass** (all corpora verbatim): the layered verdict above. The arc itself is the
   argument for the verdicts-name-their-instrument convention.
