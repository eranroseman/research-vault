# `adhd` pilot — head-to-head on #62

Primary source for the half-2 answer in [#80](https://github.com/eranroseman/knowledge-harness/issues/80).
Throwaway branch, never merged to `main` — same treatment as `prototype/archify-comparison`.

Run 2026-09-03 against `UditAkhourii/adhd` at pinned commit `53ab557`, `skills/adhd/SKILL.md`.

## What was tested

`adhd`'s adoption gate, as recovered from #58: *"one pilot on a real design question before roster
entry."* Framed as #86 framed archify's gate — half 1 is "does a need exist the current skills do
not fill", half 2 is "does the candidate fill it", answered by demonstration rather than argument.

The pass criterion, set before the run: **one non-obvious-but-viable candidate that the single-shot
answer did not produce**, judged by the author, not by a model. That is the only thing `adhd`
claims which nothing else on the roster does.

## The question

[#62 — Setup/materialization mechanism decision](https://github.com/eranroseman/knowledge-harness/issues/62).
Chosen because it is genuinely open-ended (its own body carries a "Not yet specified" section), it
is central to the map's destination, and it already has a known incumbent answer — a
`setup-matt-pocock-skills`-shaped prompt-driven wizard — so a divergence instrument has something
to beat rather than a blank page.

Both arms received a byte-identical problem statement, including the incumbent answer, the settled
constraints, and the list of what must be materialized. See `runner.js`.

## Method

Faithful to the skill body rather than to its spirit:

- **Phase 1, diverge.** 5 frames picked by `adhd`'s own rule for code-shaped problems — 4 tagged
  `code`/`design` plus 1 `wild`: `3am on-call`, `remove the load-bearing assumption`, `logistics`,
  `inversion`, `biology`. Vantage prompts copied verbatim from the skill's frame table. 5 parallel
  isolated agents, 6 ideas each, generator instruction verbatim, evaluation forbidden. The
  isolation invariant holds: no branch saw another's output.
- **Phase 2, focus.** One critic scoring novelty/viability/fit 0–10 and flagging traps, then
  clustering by underlying angle. The weighted rank — novelty 0.35 + viability 0.40 + fit 0.25 —
  is computed **in the script, not by the model**, so the ranking is mechanical as the skill
  specifies. Top 3 non-trap survivors deepened by 3 further agents.
- **Baseline arm.** One agent, same problem, same tool access, no frame and no divergence mandate.
  Ran concurrently with phase 1, so it could not see any of it.

## Cost, measured

10 agent calls (1 baseline + 5 diverge + 1 critic + 3 deepen), 296,537 subagent tokens, 51 tool
calls, 887 s wall clock for both arms. `adhd`'s own body predicts ~10 calls and 5–10× a single
answer; the run matches its stated cost.

30 ideas from 5 frames. Critic flagged **16 traps of 30** — a 53% prune rate.

## Result

`baseline-answer.md` and `adhd-result.json` are the raw arms. What follows is a reading of them,
not a substitute.

**The baseline is strong, and that matters for the verdict.** It read the live filesystem, settled
on a manifest-driven `plan`/`apply` convergence engine shipped as a skill folder, and produced five
concrete gotchas from the real tree — mixed relative/absolute symlinks that bake in the username, a
restore loop that enumerates three of four authored skills, `tomllib` being read-only, Codex writing
`last_revision` back into `config.toml`. A pilot that beat a weak baseline would prove nothing.

**Where the two arms overlap:** executable core with prompt wrappers; the private repo as an
argument rather than a package source; plugins needing real CLI calls rather than declarations.
`adhd`'s third-ranked survivor is essentially the baseline's answer.

**Where `adhd` went somewhere the baseline did not** — the candidates for the pass criterion:

1. **Materialize assertions, not files** (rank 2, N8 V7 F9, from `remove the load-bearing
   assumption`). ~60 independently owned facts, each applied and repaired alone, with
   `settings.json` a render nobody owns end to end. The baseline is file-centric throughout —
   per-file strategies plus an `owned_keys` list. This dissolves the file as the unit of ownership.
   Its deepening names the load-bearing risk precisely: an assertion cannot distinguish "this
   drifted" from "the human changed it deliberately" without a recorded last-applied value.
2. **Ship only holes, plus a release gate** (rank 1, N8 V7 F10, from `inversion`). The public
   package carries topology, fence markers, schema and ownership rules — no content — with a CI gate
   that fails the release if any private byte appears in the tarball. The baseline ships bundled
   seed templates as layer 0. The leak gate is an artifact neither the incumbent nor the baseline named.
3. **`chezmoi`'s model**, surfaced during deepening. An existing tool that already does content-free
   materialization with per-entry receipts. Neither arm's generation phase named prior art; that the
   focus pass reached for it is the "should this be built at all" question, and nothing else in
   this map's roster asks it here.
4. **The provocation, which is the strongest single output.** Every idea in the pool assumes
   authored content drifts and the vendor is stable. `.drift-state.json` says the opposite — five
   findings are `cli-behind` or `marketplace-behind`. So a materializer that pins content becomes a
   **downgrade tool** that faithfully restores a schema the CLI no longer reads, and reports success.
   Its sharper half: the 1-shared-line-in-60 diff between `~/.claude/CLAUDE.md` and
   `~/.codex/AGENTS.md` is evidence that cross-harness parity is not achievable — Codex has no
   `skillOverrides` mechanism at all — so the shipped artifact might be a **capability map**, each
   assertion tagged with which harness can enforce it, which can only be told in prose, and which
   will silently ignore it.

**Traps worth the run on their own.** The critic killed the shadow-HOME cutover and the
fresh-generation-directory rename against a measured fact — `HOME` holds a 2.6 GB sqlite with live
WAL files, 160+ session transcripts, and credentials, so flipping the tree is not available. It
killed the boot-hook idea structurally: a plugin hook cannot fire before `settings.json` and
`enabledPlugins` exist. And it killed synapse-pruning by naming a specific casualty — it would cull
`grilling`, which is deliberately kept installed-but-rarely-fired via `skillOverrides`.

## Caveats, recorded so the verdict is not read as stronger than it is

- **This is one run on one question.** `adhd`'s frame picking is deliberately varied across
  sessions, so the same problem re-run produces a different candidate set. Nothing here generalizes
  to a second problem.
- **Not apples-to-apples on depth.** The baseline was free to write as much as it wanted; the
  generators were mandated to emit one-phrase ideas. Breadth versus depth is what the two
  instruments are *for*, but it means "the baseline's answer is more implementable" is not evidence
  against `adhd`.
- **The scoring is a model judging its own pool.** Novelty/viability/fit are LLM judgements. Only
  the weighting and the ranking are mechanical.
- **Upstream's own evals remain unverified** — self-published LLM-judge results on six problems.
  This run does not corroborate them; it is a separate, local, single observation.

## Reproduce

`runner.js` is the exact workflow script, unedited. Re-run with the Workflow tool:

```
Workflow({scriptPath: "prototype/adhd-pilot/runner.js"})
```

Frame selection is fixed in the script rather than sampled, so a re-run varies only by model
sampling, not by frame set. `run-stats.json` holds the measured agent count, token total and the
runner's own progress log.
