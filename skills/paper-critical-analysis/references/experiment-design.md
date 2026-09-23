# Background: designing an experiment

## What the Summary reports

Participants (selection, characteristics); materials; procedure; design — independent and dependent variables, how each is defined and measured, which design type below, how order effects were handled; whether a pilot was run; sample size relative to similar published experiments.

## Reconstruct the design

Identify:

- Prospective, retrospective, cross-sectional, longitudinal, experimental, or observational structure
- Recruitment or sampling frame
- Experimental/observational unit
- Pairing, nesting, clustering, repeated measures, sites, batches, and time
- Allocation, concealment, blinding, matching, or weighting
- Primary and secondary outcomes
- Prespecified versus exploratory analyses

## What the design can support as a causal claim

Ranked, strongest first:

1. RCT (random assignment)
2. Quasi-experiment (natural treatment + control, no random assignment) — diff-in-diff, regression discontinuity, interrupted time series
3. Instrumental variable / propensity score — observational, resting on strong assumptions
4. Cross-sectional regression — confounders controlled statistically

At every rung the **counterfactual** should be articulated: what would have happened to the treated group absent treatment?

## Design types

Between-subjects, matched-groups, factorial, converging-series, and:

- Within-subjects — exposure itself changes behavior (learning, fatigue, maturation). Mitigated by counterbalancing or, with many values, a Latin square; counterbalancing leans on the symmetrical-transfer assumption, so ask whether that is reasonable for this task.
- Single-variable, two-level (experimental vs. control) — says nothing about whether a numeric relationship is linear.

The independent variable's range should be wide enough to show an effect and realistic for the setting; a pilot is where that is established.

## The four validity threats

- **Internal** (bias control) — does the design support the causal claim? Watch for: history, maturation, selection, attrition, instrumentation, regression to the mean, and testing. Which variables move with the one the paper credits, and does anything rule them out? Is there a control group? Were participants self-selected? Was randomization used when feasible, and was it adequate? Was allocation concealed? Were groups similar at baseline? Was blinding implemented when feasible? Was attrition minimal and balanced? Was intention-to-treat used? Were all outcomes reported?
- **External** (generalizability) — does it generalize — to whom, when, where? Is the sample representative of the target population? Are inclusion/exclusion criteria too restrictive? Is the setting realistic? Are results applicable to other populations? Are effects consistent across subgroups? Did tightly controlling variables buy internal validity at the cost of external validity?
- **Construct** (measurement) — does the measure capture the concept? Every variable should be operationalized explicitly enough for others to repeat the experiment — how it's measured, in what units, with what precision — and vague constructs are where to look first: how did the authors define the key independent and dependent variables, and do you agree with the definition? Validated instruments should be used where they exist, citing the validation study; a new scale should be piloted, with reliability (Cronbach's α ≥ 0.7 minimum, ω better) and validity (content, construct, criterion) formally checked. Were assessors blinded? Were exposures measured accurately? Was the timing of measurement appropriate?
- **Statistical conclusion** — power, multiple comparisons, and assumption violations. The assumed effect size should be stated with **why** (prior literature, smallest effect of interest, pilot data) — not "d=0.5 because that's medium." Watch for a very small sample or an inappropriate statistical test.

## Reporting red flags

- Selective outcome reporting
- No study registration/protocol
- Missing methodological details
- Results don't match methods

## Trace every denominator

Reconcile:

- Eligible, enrolled, assigned, treated/exposed, followed, measured, and analyzed units
- Outcome-specific denominators
- Exclusions before and after allocation or measurement
- Missing values and reasons
- Complete-case, imputed, weighted, or model-based analysis populations
- Figure, table, abstract, text, and supplement totals
