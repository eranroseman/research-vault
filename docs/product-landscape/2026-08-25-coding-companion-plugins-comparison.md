# Coding-companion plugins: obra/superpowers vs mattpocock/skills

Comparison note, 2026-08-25. Question asked by the author: which of the two works better as the
coding companion for knowledge-harness, and what would switching from superpowers to mattpocock
cost — assuming all in-flight work done and one-time churn free, so the answer weighs steady state
only.

**Verdict (2026-08-25): superpowers stays the coding companion; the hybrid already running (both
installed, superpowers owning the dev-process lifecycle, mattpocock owning tracker/domain hygiene)
is the correct division of labor.** The full-repo review strengthened the incumbent: mattpocock's
only per-task execution engine is beta and reviews once at the end, while this repo's just-closed
batch demonstrated that per-task review rounds and receiving-review discipline are where its
defects get caught. Two real superpowers frictions are named below with mitigations, and one flip
trigger is recorded.

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

## Recommendations

- Keep the hybrid; switch nothing off.
- Upgrade superpowers 6.2.0 → 6.3.0 as a deliberate reviewed event — it codifies three practices
  this repo hand-built (controller self-ruling, conflict ledgers, non-destructive worktree
  cleanup).
- Adopt from mattpocock's uninstalled set where useful: `to-tickets`/frontier for tracker-side
  planning, `code-review` as a second-opinion axis beside superpowers' review, `diagnosing-bugs`,
  `ask-matt` as router. None requires displacing anything.
- The superpowers upstream filing already queued (adjudicate-residuals includes Concerns; workspace
  deletion gated on dispositions) stands; v6.3.0's non-destructive cleanup reduces but does not
  remove its motivation.
