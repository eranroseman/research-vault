export const meta = {
  name: 'adhd-pilot-issue-62',
  description: 'Pilot adhd against a baseline single-shot on the setup/materialization design question',
  phases: [
    { title: 'Diverge', detail: 'baseline single-shot + 5 isolated frame generators' },
    { title: 'Critic', detail: 'score, flag traps, cluster' },
    { title: 'Focus', detail: 'deepen the top 3 survivors' },
  ],
}

const PROBLEM = `How should a cross-harness developer plugin materialize an entire authored agent harness onto a fresh machine in one command?

What it must materialize:
- ~/.claude/settings.json (permissions, hooks, statusline, enabledPlugins, skillOverrides)
- a user-level ~/.claude/CLAUDE.md and a ~/.codex/AGENTS.md (currently kept as hand-maintained copies)
- ~/.codex/config.toml
- a set of third-party skill installs plus their lockfile (~/.agents/.skill-lock.json)
- the symlink topology ~/.codex/skills -> ~/.claude/skills -> ~/.agents/skills
- installed plugins from a marketplace

Constraints that are already settled and not up for debate:
- It must work on BOTH Claude Code and Codex.
- It must be idempotent and safely re-runnable as DRIFT REPAIR, not a one-shot installer.
- The private repo holding the user's installed configuration stays private and is not the package source.
- Detecting drift is a separate concern; this is about materializing and repairing.

The known incumbent answer, for reference: a prompt-driven human-in-the-loop wizard - detect existing state read-only, present findings section by section each with an accept-in-one-word default, show a draft of every file about to be written, let the user edit, materialize from bundled seed templates, idempotent on re-run.`

const IDEAS = {
  type: 'object',
  properties: {
    ideas: {
      type: 'array',
      minItems: 6,
      maxItems: 6,
      items: {
        type: 'object',
        properties: {
          text: { type: 'string', description: 'One phrase or one sentence. The idea itself.' },
          rationale: { type: 'string', description: 'One line: why this frame produces this idea.' },
        },
        required: ['text', 'rationale'],
      },
    },
  },
  required: ['ideas'],
}

const CRITIC = {
  type: 'object',
  properties: {
    scored: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          text: { type: 'string' },
          frame: { type: 'string' },
          novelty: { type: 'number', description: '0-10, distance from the obvious default' },
          viability: { type: 'number', description: '0-10, could it actually ship' },
          fit: { type: 'number', description: '0-10, does it address the stated problem' },
          trap: { type: 'boolean', description: 'Attractive but a trap: hidden cost, false economy, will not scale, premature abstraction' },
          trapReason: { type: 'string', description: 'One line. Empty if not a trap.' },
        },
        required: ['text', 'frame', 'novelty', 'viability', 'fit', 'trap'],
      },
    },
    clusters: {
      type: 'array',
      minItems: 3,
      maxItems: 6,
      items: {
        type: 'object',
        properties: {
          label: { type: 'string', description: 'Label by underlying angle, not surface keyword' },
          ideas: { type: 'array', items: { type: 'string' } },
        },
        required: ['label', 'ideas'],
      },
    },
    provocation: { type: 'string', description: 'One wildcard question or idea that opens a new direction' },
  },
  required: ['scored', 'clusters', 'provocation'],
}

const DEEPEN = {
  type: 'object',
  properties: {
    idea: { type: 'string' },
    sketch: { type: 'string', description: '4 to 8 sentences on how it would actually work' },
    loadBearingRisk: { type: 'string' },
    firstStep: { type: 'string', description: 'The first concrete step a builder would take' },
    childIdeas: { type: 'array', minItems: 3, maxItems: 5, items: { type: 'string' } },
  },
  required: ['idea', 'sketch', 'loadBearingRisk', 'firstStep', 'childIdeas'],
}

// Frames picked per adhd's rule for code-shaped problems: 4 tagged code/design + 1 wild.
const FRAMES = [
  {
    key: '3am-on-call',
    vantage: 'You are the on-call engineer woken at 3am when this breaks. What design would let you not get paged?',
  },
  {
    key: 'remove-load-bearing-assumption',
    vantage: 'Name the thing everyone treats as fixed (framework, database, request-response model, network). Imagine it is gone. What is possible?',
  },
  {
    key: 'logistics',
    vantage: 'Steal mechanisms from logistics: queues, batching, just-in-time, hub-and-spoke, returns, last-mile. Apply them literally.',
  },
  {
    key: 'inversion',
    vantage: 'Ask the OPPOSITE question. If the goal is X, brainstorm how to guarantee NOT X. Then negate each answer back.',
  },
  {
    key: 'biology',
    vantage: 'Transplant a mechanism from biology (immune systems, neural plasticity, cell signaling, evolution, gut flora). Force-fit it onto this engineering problem.',
  },
]

const GENERATOR_INSTRUCTION = `You are in DIVERGENT mode. You are a generator, not a critic.
Generate 6 short distinct ideas under this frame. Each idea is one phrase or one sentence.
Do not evaluate. Do not rank. Do not hedge.
The first three obvious answers everyone would give are banned.
Push past them into the awkward middle.`

phase('Diverge')

// Arm A (baseline, the incumbent) and Arm B phase 1 (isolated frame generators) run concurrently.
// The barrier is required: the critic scores and clusters across the FULL pool.
const divergeResults = await parallel([
  () => agent(
    `${PROBLEM}\n\nAnswer this design question as well as you can. Recommend a mechanism and justify it. This is a single-shot answer: give your best thinking in one pass, the way a senior engineer would answer if asked directly. Be concrete and specific.`,
    { label: 'baseline:single-shot', phase: 'Diverge' }
  ),
  ...FRAMES.map(f => () => agent(
    `PROBLEM:\n${PROBLEM}\n\nYOUR FRAME:\n${f.vantage}\n\n${GENERATOR_INSTRUCTION}`,
    { label: `diverge:${f.key}`, phase: 'Diverge', schema: IDEAS }
  )),
])

const baseline = divergeResults[0]
const pool = FRAMES.map((f, i) => ({ frame: f.key, result: divergeResults[i + 1] }))
  .filter(p => p.result)
  .flatMap(p => p.result.ideas.map(idea => ({ ...idea, frame: p.frame })))

log(`Diverge complete: ${pool.length} ideas from ${pool.length ? new Set(pool.map(i => i.frame)).size : 0} frames`)

phase('Critic')

const critic = await agent(
  `You are in FOCUS mode, acting as the critic over a divergent idea pool. You did not generate these; judge them cold.

PROBLEM:
${PROBLEM}

IDEA POOL (${pool.length} ideas, each tagged with the cognitive frame that produced it):
${pool.map((it, i) => `${i + 1}. [${it.frame}] ${it.text} — ${it.rationale}`).join('\n')}

Do three things:
1. SCORE every idea on novelty (distance from the obvious default), viability (could it actually ship), and fit (does it address the stated problem), each 0 to 10. For any idea that looks attractive but is a TRAP — hidden cost, false economy, will not scale, premature abstraction — set trap true and give a one-line reason.
2. CLUSTER the ideas into 3 to 6 groups by their underlying angle, not by surface keywords. Label each cluster by its angle.
3. Give one PROVOCATION: a wildcard question or idea that opens a direction none of these took.

Score honestly. An idea that is merely a restatement of the incumbent wizard answer scores low on novelty.`,
  { label: 'critic:score-cluster', phase: 'Critic', schema: CRITIC }
)

// adhd's weighting, computed mechanically rather than asked for: novelty .35 + viability .40 + fit .25
const weight = s => 0.35 * s.novelty + 0.40 * s.viability + 0.25 * s.fit
const survivors = (critic?.scored ?? [])
  .filter(s => !s.trap)
  .sort((a, b) => weight(b) - weight(a))
const traps = (critic?.scored ?? []).filter(s => s.trap)
const top3 = survivors.slice(0, 3)

log(`Critic: ${survivors.length} survivors, ${traps.length} traps flagged. Deepening top 3.`)

phase('Focus')

const deepened = await parallel(top3.map(s => () => agent(
  `You are in FOCUS mode. Take one promising idea and connect dots.

PROBLEM:
${PROBLEM}

THE IDEA: ${s.text}

Sketch how it would actually work in 4 to 8 sentences. Name the load-bearing risk. Name the first concrete step a coder would take. Then generate 3 to 5 sub-ideas that branch off (variations, combinations with other domains, things this unlocks).`,
  { label: `focus:${s.text.slice(0, 40)}`, phase: 'Focus', schema: DEEPEN }
)))

return {
  baseline,
  poolSize: pool.length,
  frames: FRAMES.map(f => f.key),
  clusters: critic?.clusters ?? [],
  provocation: critic?.provocation ?? '',
  scored: (critic?.scored ?? []).map(s => ({ ...s, weighted: Number(weight(s).toFixed(2)) })),
  traps,
  top3: top3.map(s => ({ ...s, weighted: Number(weight(s).toFixed(2)) })),
  deepened: deepened.filter(Boolean),
}
