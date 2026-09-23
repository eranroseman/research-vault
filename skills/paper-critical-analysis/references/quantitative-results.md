# Background: interpreting quantitative results

## Order of assessment

Assess methods and statistics in this order: question and target quantity; design and unit of inference; sampling, allocation, controls, masking, and timing; sample-size or precision rationale; inclusion, exclusion, attrition, and missingness; analysis–design alignment and assumptions; multiplicity and prespecification; effect estimates, uncertainty, denominators, and harms; interpretation, causality, and generalizability.

## Reading the numbers

- Charts: error bars typically span two standard errors. Watch for distorted axes or a truncated y-axis exaggerating differences.
- For factorial designs, check main effects and interactions.
- All p values should be reported, not only those below a threshold, and the wording should be "statistically significant": a statistically significant result can still carry no practical consequence.

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
