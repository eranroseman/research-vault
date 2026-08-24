# Slice decision rules — pre-registered

Registered 2026-08-22, before Phase 2 evidence exists. Shape adopted from Memoria's decision_rules discipline: every blocker written down before its evidence arrives — metric, window, threshold, recommendation — so a rule the author can read today cannot be quietly re-derived once the numbers are in. **A rule recommends; it never acts.** Assessment is deterministic (anyone may compute it); application is the author's, at the named moment. The registry CLOSES when Phase 2 starts: rules may be amended or added only before their evidence window opens.

Why: §9's falsified-when ("the author routed around the vault") and validated-when ("the author judges the brief defensible") are self-assessments, in a single-run experiment, made by the builder. These rules make the first countable and give the second a floor it must clear.

```yaml
- id: routed-around-tagging
  blocker: the routing-around falsification clause is builder-judged and retrospective
  metric: findings-log entries tagged `routed-around` — vault-owned work the author
    performed outside the vault, tagged AT OCCURRENCE, not in hindsight
  window: the whole slice (both sessions)
  threshold: ">= 1 tagged entry"
  recommendation: the §9 falsified-when clause fires mechanically — record the
    falsification as such, do not soften (Plan S global constraint already forbids
    softening; this rule removes the judgment about whether an occurrence "counts")
  check: grep for the tag over research/validation-slice/2026-08-22-slice-findings.md
  status: registered

- id: inbox-review-sizing
  blocker: rubber-stamp / inbox-rot pressure is the leading indicator of routing-around,
    and nothing measures it (Memoria analogue - evidence-review-sizing)
  metric: per session, review-inbox entries created (non-SKIPPED, per batch item 16)
    vs entries receiving a disposition (ack or fix) by the end of the FOLLOWING session
  window: each slice session, assessed at slice end
  threshold: ">= 10 created in one session AND < 50% dispositioned"
  recommendation: "simplify the gate" — a per-check-class review under the §6 warn-tier
    precision doctrine (tune or demote the noisiest class), fed by the §9 measured
    inbox-precision output; NOT a falsification by itself
  check: count entry lines vs ack lines in inbox/review-queue.md, bucketed by session
  status: registered

- id: defensibility-floor
  blocker: "the author judges the brief defensible" is an unanchored self-assessment
  metric: the validated-when mechanical criteria (claim resolution rate, verified events,
    drill catches with leg attribution, inbox precision from the drill's valid arm)
  window: the judgment step
  threshold: the author's defensibility judgment MAY NOT be recorded as a pass while any
    mechanical criterion stands failed against remediated gates — the self-assessment has
    a floor; above the floor it remains the author's call
  recommendation: if judged defensible below the floor, record the divergence explicitly
    (which criterion failed and why the author overrode) — an override is data, never silent
  check: the Plan S judgment checklist itself
  status: registered
```

Cost honesty: this file plus the tagging habit is the whole cost. No harness code changes — clear of the pre-slice instrument freeze, the trust-core remediation gate, and Plan Q.
