# Background: quantitative methods

Loads when the paper reports a quantity it measured, or a statistic it computed from data. The report's section 2.2 (Method) draws on "What the Summary reports" below, and stage 2 walks the file for N entries; the judge reads it for Credibility, Generalizability and Assumptions.

## What the Summary reports

Participants (selection, characteristics); materials; procedure; design — independent and dependent variables, how each is defined and measured, which design type below, how order effects were handled; whether a pilot was run; sample size relative to similar published experiments.

## Order of assessment

Assess methods and statistics in this order: question and target quantity; design and unit of inference; sampling, allocation, controls, masking, and timing; sample-size or precision rationale; inclusion, exclusion, attrition, and missingness; analysis–design alignment and assumptions; multiplicity and prespecification; effect estimates, uncertainty, denominators, and harms; interpretation, causality, and generalizability.

## Reconstruct the design

Identify:

- Prospective, retrospective, cross-sectional, longitudinal, experimental, or observational structure
- Recruitment or sampling frame. **Probability** (random, stratified, cluster, multistage) — needed for population inference. **Non-probability** (convenience, snowball, purposive, quota) — fine for exploratory or qualitative work; the results should not be generalized beyond the sample. The sampling frame and any selection bias should be documented.
- Experimental/observational unit
- Pairing, nesting, clustering, repeated measures, sites, batches, and time
- Allocation, concealment, blinding, matching, or weighting
- Primary and secondary outcomes
- Prespecified versus exploratory analyses

## Variables

Independent: manipulated by the researcher, with several values. Dependent: measures the behavior; it states what is measured and how, with its reliability (the same result again, and the expected error) and its validity (it measures the intended thing). Control: held constant; aids replication, but over-control hurts external validity (a quiet, well-lit lab may not mirror real use). Random: varied at random, possibly within constraints, as in random assignment against bias. Confounding: changes along with the independent variable. A sound paper defines its variables explicitly enough to replicate; some (visual complexity, stress) resist definition.

## What the design can support as a causal claim

Ranked, strongest first:

1. RCT (random assignment)
2. Quasi-experiment (natural treatment + control, no random assignment) — diff-in-diff, regression discontinuity, interrupted time series
3. Instrumental variable / propensity score — observational, resting on strong assumptions
4. Cross-sectional regression — confounders controlled statistically

At every rung the **counterfactual** should be articulated: what would have happened to the treated group absent treatment?

## Design types

- Between-subjects — each participant sees one value; no carry-over, learning, or fatigue, and sometimes the only option (age); needs more participants and equivalent groups (random assignment).
- Within-subjects — exposure itself changes behavior (learning, fatigue, maturation). Mitigated by counterbalancing or, with many values, a Latin square (each value appears in, before, and after every position equally often; the participant count is a multiple of the value count); counterbalancing leans on the symmetrical-transfer assumption, so ask whether that is reasonable for this task.
- Matched groups — a pretest on measures expected to affect behavior; the study runs longer, and the pretest may itself affect performance.
- Single-variable, two-level (experimental vs. control) — easy to interpret; says nothing about whether a numeric relationship is linear. Multi-level shows the relationship's shape at the cost of more time, participants, and analysis.
- Factorial — crosses factors; reveals interactions and gives more precise, more generalizable results; mixed when some factors are within- and some between-subjects; harder to interpret once interactions appear.
- Converging series — several experiments on one question, each fixing a level for the next or eliminating hypotheses; flexible, but interactions across experiments are hard to assess, and there is no random assignment between experiments.

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

## Reading the numbers

- Charts: error bars typically span two standard errors. Watch for distorted axes or a truncated y-axis exaggerating differences.
- For factorial designs, check main effects and interactions.
- All p values should be reported, not only those below a threshold.
- Histograms show whether the data looks normal enough for the test used.
- Bars for a categorical independent variable, lines for a numeric one; scatterplots show whether two variables are related, with a correlation coefficient for strength.
- Crossover interactions may show no main effect.

## Analysis–design alignment

Ask whether the method accounts for:

- Outcome scale and distribution
- Pairing and repeated measures
- Clustering and multilevel structure
- Unequal follow-up, censoring, or competing events
- Sampling weights or matched designs
- Baseline adjustment and prespecified covariates
- Multiplicity and outcome hierarchy
- Model tuning and validation
- Missingness assumptions

The name of a statistical test is not enough: the paper should state inputs, model form, uncertainty method, software/version, and relevant diagnostics.

Prefer, in the paper's reporting:

- Effect or performance estimates with units, not p-values alone
- Compatible uncertainty intervals, interpreted appropriately
- Absolute as well as relative quantities when decision-relevant
- Exact denominators and analysis sets
- Assumption and sensitivity context
- Clinical, biological, policy, or practical relevance distinct from statistical compatibility

## Sample size, multiplicity, missing data

Sample size and precision — look for: prospective calculation or precision rationale; target effect or interval width; variance, event rate, prevalence, or accuracy assumptions; Type I error, power, sidedness, and multiplicity when applicable; design effect, clustering, attrition, noncompliance, and missingness. An imprecise result is read off the estimate and its uncertainty; observed or post hoc power answers nothing here.

Multiplicity — identify the inferential family before expecting adjustment: multiple primary outcomes; multiple intervention arms or contrasts; repeated time points; subgroups and interactions; interim analyses; high-dimensional features; model selection.

Missing data — check: missingness by group, variable, outcome, and time; reasons and relation to intercurrent events; information used by imputation or weighting; compatibility of imputation and analysis models; sensitivity to plausible departures from assumptions.

## Assumption diagnostics

For each model: linearity, normality (residuals), homoscedasticity, independence; multicollinearity (VIF); influential observations (Cook's distance, leverage); was the appropriate model used?

Parametric tests (t-test, ANOVA) assume a normally distributed population, and some also require sphericity. Where a parametric test was used, look for the check of the assumption it depends on.

## Claim–evidence mismatches

- Causal wording from an observational or otherwise non-identifying design
- Mechanistic conclusions supported only by association or prediction
- Conclusions based on a secondary, exploratory, or post hoc outcome without labeling
- Directionally correct claims that overstate magnitude or precision
- Population, setting, intervention, comparator, outcome, or time-horizon extrapolation
- "No effect," "equivalent," or "safe" conclusions from imprecise or non-significant results
- Abstract or conclusion claims that omit material harms, uncertainty, subgroup caveats, or null findings

## Analysis biases to watch for

- **P-hacking** — collecting data until significance is reached; testing multiple outcomes and reporting only the significant ones; trying multiple analysis methods; excluding "outliers" to reach significance; slicing subgroups until one is significant. Detection: p-values suspiciously just below .05; many researcher degrees of freedom; undisclosed analyses.
- **HARKing** — presenting post hoc hypotheses as if they were predicted a priori.
- **Base rate neglect** — ignoring prior probability when evaluating evidence.
- **Regression to the mean** — treatment effects in extreme groups may be regression artifacts.
- **Texas sharpshooter fallacy** — selecting the data after seeing the pattern.
