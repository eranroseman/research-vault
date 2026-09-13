# Rethink audit — the multi-agent development process (methods-template)

Disposition: historical (2026-09-06)

**Verified (2026-08-25):** first pass (design/gap/migrate/trade-offs) drafted, then adversarially reviewed
through four independent lenses (invented-redesign, completeness, evidence-grounding, prior-art-fidelity).
Three findings survived and are folded into this version, not the discarded draft: (1) a proposed
"controller/orchestrator two-adapter seam" rested on a misattributed quote and a reused sentence from a
different requirement — withdrawn, deferred instead to
[the sibling controller-protocol audit](2026-08-25-controller-protocol-rethink-audit.md), which researched
that exact seam directly; (2) requirement 14's "two independently-reasoning seats converged" claim was false
— both citations trace to the same seat (the reconstruction note's own section header says so) — corrected to
match the sibling audit's independent finding that the delegation rule's reversibility condition is asserted,
not anchored; (3) requirement 9's proposed structural hardening (read-only audit tooling) had no observed
failure behind it and was withdrawn as manufactured redesign, per this method's own stated risk. One gap
(transcript preservation, requirement 18) closed during this audit's own runtime, by a concurrent session —
confirmed against `docs/research/raw/2026-08-25-transcript-archive-manifest.md` before being marked closed rather
than assumed from the reconstruction note's now-stale claim.

Audit target: the spec-driven, multi-agent-LLM development *process* used to build the research-vault
plugin — not the vault product it built. Consumers: workload 2 (analysis/reports), workload 3 (PKM daily
loop), a possible research-vault-as-paper methods section, and the single human author across all of them. Method:
rethink-audit (requires → prior-art → design → gap → migrate → trade-offs). Primary sources:
[the process reconstruction](../2026-08-25-plugin-development-process-reconstruction.md),
[the pre-slice batch method retrospective](../../superpowers/specs/2026-08-16-foundation-spec-pre-slice-batch-method-results.md),
[prior art for eight of the process's mechanisms](../prior-art/2026-08-25-ai-agent-process-design-prior-art.md),
the foundation spec, and `docs/superpowers/plans/2026-08-22-slice-decision-rules.md`.

## requires:

**Callers swept:** workload 2 and workload 3 builds (template reuse; domain-specific assumptions must be
visible, not silently carried over) — `caller`. The research-vault-as-paper methods section, if it happens —
`caller`. The single human author, the one non-scalable resource — `caller`/`docs`. Multiple stateless LLM
seats (controller, implementer, reviewer, orchestrator) sharing no context or artifact by default — `docs`. A
future public reader or collaborator, per the spec's own "written for a reader with no shared history" line
— `docs`/`assumed`.

**Could not reach:** session transcripts (unversioned, an admitted gap in the source note itself); other
authors or model families running this process (n=1 on both axes, self-named); live use of workload 2/3 (not
yet run); the exact population the "163 short-form-approval-turns" measurement covers (an open
scope-of-instrument question in the source's own words).

**21 requirements**, each evidence-tagged, spanning: turning ambiguity into citable decisions before build
(1); a spec that absorbs decisions until deletable (2); an ADR bar reserving constitutional weight, where
rejection ≠ lost decision (3); adversarial verification with counted findings, verifier ≠ producer (4);
pre-registered decision rules, frozen at window-open, advisory-only (5); conserving the human's decision
budget as agent count scales (6); coordinating stateless seats despite brief-currency decay (7);
discrimination proof as the unit of review evidence (8); audits as read-only, fresh-refuting-verifier
artifacts (9); vendored-code provenance with sidecar corrections (10); rulings recorded where the next reader
looks (11); correct-forward over amend (12); consent-bearing acts staying with the seat that holds the context
(13); a four-condition delegation-without-reasking gate (14); enumerate exceptions, don't count them (15);
method retrospectives amended visibly (16); domain transfer without silent assumption-carrying (17); durable
preservation of ruling reasoning (18); resolving or instrumenting the catch-latency-vs-quality disagreement
(19); bounding doc drift to three end states (20); staying legible to a reader with no shared history (21).

## prior-art:

Eight mechanisms checked against primary sources, judged specifically against this process's actual
population — one human, many stateless LLM seats — not the population most cited sources were built for. Full
citations: [the prior-art note](../prior-art/2026-08-25-ai-agent-process-design-prior-art.md).

- **Spec-as-amendable-contract** — matches Nygard's ADR pattern and Adzic's living-documentation goal; IETF's
  RFC process is the opposite mechanic (immutable-plus-successor), cited as contrast. Gap: all three assume a
  human reader with continuity; this process's stateless-agent-reads-it-cold constraint is unnamed in any of
  them.
- **Decision-budget economics** — no clean citation. Decision-fatigue literature is contested (a 23-lab
  registered replication found d=0.04, indistinguishable from zero). Better fits: Parasuraman/Sheridan/
  Wickens' automation-taxonomy (which decisions escalate to the human), NASEM's human-AI-teaming report,
  Atlassian's DACI (closest shape, but built for named accountable humans, not stateless seats).
- **Adversarial verification with counted findings** — the best-covered mechanism: AI-safety-via-debate,
  multiagent debate, LLM-as-judge (with its self-enhancement-bias caveat, which is the actual reason "a fresh
  agent instructed to refute" beats re-asking the same one), Anthropic's own measured 90.2% multi-agent gain,
  chaos engineering, red-team practice, Kahneman-style adversarial collaboration. One process-specific
  extension beyond all of them: publishing the confirmed/refuted tally itself as the artifact.
- **Pre-registered decision rules** — strong non-AI analogs (Nosek, Chambers' Registered Reports, ICH E9's
  SAP-freeze). AI-eval-specific pre-registration is a **named gap**, not a citation. "Advisory only" — a rule
  that can't act — is this process's own addition; none of the cited instruments could act even if they
  wanted to.
- **Audits as read-only artifacts** — matches AICPA/SOC 2 auditor independence (structurally barred from
  remediating), blameless-postmortem doctrine, RFC 6962's append-only logs. All three enforce this on
  accountable, persistent actors; this process's audit agents have no persistent stake, so the discipline
  currently rests on instruction-following, not structure.
- **Vendored-code provenance** — SLSA/in-toto/SBOM fit the build-pipeline case; the sharpest match is
  Debian's `3.0 (quilt)` format (patches sidecar beside a never-edited pristine upstream), run at
  full-distribution scale for over a decade with no agents involved at all.
- **Multi-agent topology** — the one item needing 2024–2026 sources. Cognition's "Don't Build Multi-Agents"
  names the shared-artifact failure and calls it unsolved (mid-2025); MetaGPT and Anthropic's own multi-agent
  post converge independently on the identical "telephone game" metaphor this process's own ledger uses; a
  2026 CMU paper (CAID) reaches merge-triggered task-graph replanning but not per-brief regeneration. No
  source closes the specific "brief goes stale between authoring and dispatch" failure — this process's own
  fix appears to sit ahead of the published record on that one point, and only that one point.
- **Discrimination-proof-as-test-evidence** — squarely mutation testing (DeMillo/Lipton/Sayward's coupling
  effect, Just et al.'s mutant-validity finding, Google's diff-scoped mutation-in-review practice).

## design:

Applying codebase-design's vocabulary loosely: seats and artifact-producing stages are modules; a brief,
ruling, or finding crossing from one to the next is a seam; the invariant at each seam is what the receiving
module must be able to trust without re-deriving it.

Walking all 21 requirements against the two source ledgers plus the prior-art note, **14 requirements are
already the first-principles answer, with no redesign content warranted**: 1 (wayfinder→spec citation), 2
(dated-entry spec contract), 3 (ADR bar, rejection lands as prose), 4 (counted adversarial verification), 9
(audits are read-only in practice — see correction below), 10 (vendored-code sidecar provenance), 11 (rulings
in commit history), 12 (correct-forward), 13 (consent stays with the context-holder), 14 (delegation gate —
see correction below), 15 (enumerate not count), 16 (retrospectives amended visibly), 21 (legible to a cold
reader).

Two of these carry a caveat worth stating plainly rather than silently omitting:

- **Requirement 5** (pre-registration): sound and standing, but AI-eval-specific pre-registration is a named
  gap in the field, not a matched citation, and "advisory only" is this process's own unvalidated addition —
  nothing yet has ever tested what happens if an agent seat treats a rule's recommendation as license to act.
  No failure has been observed, so no new mechanism is warranted now; this is a thing to watch, not a gap to
  close.
- **Requirement 9** (read-only audits): the first draft proposed restricting audit dispatch to read-only
  tools as a structural hardening. On adversarial review, that doesn't survive: no source or ledger entry
  shows this discipline ever failing — the 39/21/18 no-fabrication tally is evidence the *finding-quality*
  check works, not that the *read-only* boundary was ever crossed. The same "other domains enforce this
  structurally" argument would justify hardening every instruction-following safeguard in the process (the
  ADR bar, correct-forward, enumerate-don't-count) — an argument this audit method's own boundaries warn
  against manufacturing. Corrected: requirement 9 is MET, full stop; structural enforcement is a trade-off to
  revisit only if a violation is ever observed.
- **Requirement 8** (discrimination proof) is MET but the first draft wrote it up as "nothing to add" while
  quietly adding real content — the retrospective's own admitted gap that only the *reader's* re-measurement
  half of review currently works reliably, not the *writer's* duty to state a finding's instrument and scope.
  That's a genuine, source-grounded, narrow addition (matching the treatment reqs 5/7/20 already got), not a
  silent one.
- **Requirement 14** (four-condition delegation gate): the first draft called this the audit's strongest
  evidence — "two independently-reasoning seats converged on the identical rule." That's wrong: the
  reconstruction note's own section header states items 17–26, including the ledger citation for this rule,
  are all "the implementer seat's counted testimony" — the same seat as the retrospective. Both citations
  trace to one seat, not two. Corrected: the mechanism is MET and standing, but its reversibility condition is
  asserted, not anchored — confirmed independently by the sibling controller-protocol audit, which ran a real
  five-angle prior-art search and found no anchor for reversibility anywhere. Two unrelated audits reaching
  the identical correction from different evidence is stronger confirmation than the false "convergence"
  claim it replaces.

**Six requirements have a real, small gap** (detailed under gap: below): 6, 7, 17, 18, 19, 20. None require
new modules — only re-scoping a measurement, naming a durable home for a rule that already runs, or checking
a box on a pass that already exists.

One design element from the first draft — a standing "controller/orchestrator two-adapter seam" requiring
every dispatched brief to carry an identical regenerated-and-pre-checked contract regardless of which seat
dispatches it — does not survive adversarial review and is **withdrawn**. It rested on a misattributed quote
(the "three seats... without seeing the same artifact" language is the reconstruction note's, not the
retrospective's, and names a controller/implementer/reviewer triad with no orchestrator in it) and on reusing
a sentence about decision-approval relay (requirement 6's topic) as if it were about brief-authoring
(requirement 7's topic). The actual authority is
[the sibling controller-protocol audit](2026-08-25-controller-protocol-rethink-audit.md), which researched
this exact seam directly and reached a settled, better-grounded disposition: three governing modules
(delegation-authority, authority-scoping — first-hand consent vs. relayed consent, dispute-adjudication) exist
today as one adapter each, formalization is deliberately parked pending a second controller-shaped session,
and that trigger hasn't fired. Requirement 7's design answer is: defer to that existing disposition rather
than compete with it.

## gap:

Read against the reconstruction note, the pre-slice retrospective, the controller-protocol material, and
(where cited) the live repo state.

| #   | Status                                 | Finding                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| --- | -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 6   | Gap                                    | The 163-short-form-turn decision-budget measurement has an admitted scope-of-instrument problem: most batch decisions consumed the orchestrator's relay, not the author's direct word, and nothing today distinguishes the two. Fix available off-the-shelf: the sibling controller-protocol audit already designed an authority-scoping module distinguishing first-hand from relayed consent — reuse that categorical split to re-scope the count, rather than inventing a parallel taxonomy.                                                                                                                                                                                                                                                                                                                                                                 |
| 7   | Gap, narrower than first stated        | Both halves of the brief-dispatch discipline (pre-check hand-over, ledger item 17; regeneration-before-dispatch, ledger item 18) are not merely narrated — they were checked, logged, and repeated live within the pre-slice batch's own SDD ledger (`.superpowers/sdd/2026-08-22-post-q-batch/progress.md:5822,6013-6014`; `task-22-report.md:116`). The first draft's claim that this was "never operationalized" was itself an unscoped negative — the retrospective's own central warning. The real gap: neither half has a durable home outside that one batch's ledger, unlike ledger item 19 (canary discipline), which lives in `docs/testing.md`. The controller/orchestrator seam question itself is not an open gap — it's a deliberately parked question with a named, unfired trigger (a second controller-shaped session), per the sibling audit. |
| 17  | Gap                                    | No domain-assumption register exists; the source names its own n=1-on-both-axes limit and names workload 2 as the natural test.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| 18  | Closed during this audit's own runtime | The reconstruction note (written earlier the same day) named transcript decay as an open gap. By the time this audit's migrate step reached it, `docs/research/raw/2026-08-25-transcript-archive-manifest.md` already recorded 63 sessions, fixity-hashed, archived off-repo (snapshot `e45c976`) — landed same-day, independently. Residual: no named re-snapshot trigger, so today's coverage starts decaying again the moment a new session closes.                                                                                                                                                                                                                                                                                                                                                                                                          |
| 19  | Gap                                    | The catch-latency-vs-catch-quality disagreement between the controller and execution seats is recorded, by design, as unresolved. No instrument exists to make it decidable next time.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| 20  | Gap                                    | The three-way doc-drift classification (contract-with-parity-test / register-with-triggers / deletable) is named by the source as an *unstated* target the existing absorption pass "can steer toward... instead of discovering it." The machinery (parity tests, a triggered register, a scheduled absorption pass) already exists; the explicit tag does not.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |

## migrate:

Ordered by dependency and by which gaps carry a decaying-evidence or hard-deadline cost.

1. **(18) Name a re-snapshot trigger now.** The archive exists; only its cadence doesn't. Add one line
   wherever the standing register lives: re-export on every plan/batch close, matching the cadence already
   used for `ruling:`/`plan:` commits.
2. **(6) Re-scope the decision-budget count.** Using the sibling audit's first-hand/relayed distinction,
   split the archived turns into author-direct vs. orchestrator-relayed, and pre-register that split — using
   the existing pre-registration mechanism (requirement 5) — before workload 2 opens.
3. **(19) Add a pre-registered catch-latency rule** to `docs/superpowers/plans/2026-08-22-slice-decision-rules.md`
   before Phase 2 starts — the registry's own text says it closes then, and the slice is unblocked, so this
   has a real deadline, not just a preference for doing it early. Metric: time (or dispatch-count) from a
   defect's introduction to its catch, bucketed by catching mechanism.
4. **(17) Create the domain-assumption register** before workload 2 begins — batch with step 3's deadline.
   One file naming which of the 26 ledger mechanisms are domain-general versus which spec/plan content is
   citation/vault-specific and must be re-derived, not copied.
5. **(20) Tag the absorption pass.** Add the explicit three-way classification to the absorption pass's own
   instructions (`docs/superpowers/specs/2026-08-16-foundation-spec.md:200`) so every doc surviving a pass
   gets one of the three tags; an untagged doc after the pass is itself the drift signal.
6. **(7) Give the already-operating dispatch discipline a durable home** — a file path (candidates:
   `docs/agents/`, or wherever the sibling audit's own migrate step 1 is already sharpening pointers), so
   ledger items 17 and 18 stop living only inside one batch's SDD ledger, the same way item 19 lives in
   `docs/testing.md`. Do not attempt to formalize the controller/orchestrator seam itself here — that trigger
   is already named and dated elsewhere and hasn't fired; a second competing disposition would contradict the
   single-source-of-truth discipline this whole process runs on.

## trade-offs:

- **Instruments 6, 19, and 20 spend the resource the method exists to conserve** — the author's decision
  budget — to buy legibility. Flip: if workload 2 shows per-instrument maintenance cost exceeding the number
  of rulings any of them actually change, retire the instrument rather than renew it.
- **Pre-registering 6 and 19 before Phase 2 is a hard, dated gate, not a reversible choice against "start the
  slice and derive rules from early results."** If the deadline is missed, the honest fallback is a
  disclosed, differently-trusted substitute (an independent review of the late rule against evidence it has
  already seen, labeled as such) — not silently pretending pre-registration still holds.
- **Deferring requirement 7's full formalization accepts a known, named risk**: a third stale-brief-class
  error could recur before a second controller-shaped session justifies promoting the rule into a skill.
  Flip: one more such defect landing should promote it immediately — this process already sets that
  precedent itself, ratifying the delegation rule "on the third instance," not the fourth.
- **Leaving requirements 5 and 9 as instruction-following rather than structurally enforced** trades a small
  residual risk (an agent could, in principle, act on a mere recommendation, or write during an audit) for
  not building tooling restrictions nobody has yet needed. Flip: the first *observed* instance of either
  failure mode should trigger structural enforcement immediately — not before.

**Verdict:** not "Already sound. Keep." (six real, small gaps), and not a redesign either — every gap is a
scoping, homing, or completion problem inside mechanisms the process already has right, matching the sibling
audit's own framing for the adjacent controller-seam question almost exactly.
