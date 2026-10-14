#!/usr/bin/env Rscript
# power-simr.R: power by simulation for an experiment proposal.
# Shipped by the experiment-proposal plugin as templates/power-simr.R; `design`
# copies it to proposal/power.R and fills the PARAMETERS block from the design
# brief. Everything below END OF PARAMETERS is generic and stays as it is.
#
# Models of family "lmer" and "glmer" run through simr (makeLmer or makeGlmer,
# then powerCurve along participants). Models of family "clmm" run through the
# loop at the end of this file, because simr does not simulate cumulative link
# mixed models: the latent variable is simulated, cut at the thresholds, fitted
# with ordinal::clmm, and the significant fits are counted.
#
# Prerequisites: R with lme4, lmerTest, ordinal and simr, installed by the user:
#   Rscript -e 'install.packages(c("lme4","lmerTest","ordinal","simr"), repos="https://cloud.r-project.org")'
# Run:  Rscript proposal/power.R

## ---- PARAMETERS (filled by design from the brief) ----

params <- list(
  seed = 20261013,
  n_sims = 200,            # simulations per participant count; use 1000 for the final run
  alpha = 0.05,
  target_power = 0.80,
  # Participant counts to try. Keep every value a multiple of the number of
  # between-subjects groups and of the number of counterbalanced orders.
  n_grid = c(12, 16, 20, 24, 32, 40),
  trials_per_condition = 20,
  # Within-subjects factors (every participant sees every level) and
  # between-subjects factors (equal groups, assigned round-robin): name = levels.
  within = list(device = c("mouse", "trackball")),
  between = list(),
  # One entry per dependent variable. The FIRST entry is the primary measure and
  # sets the participant count; every other model's power is reported at that count.
  #   dv       the measure's name
  #   family   "lmer" (continuous), "glmer" (trial-level 0/1), "clmm" (ordinal rating)
  #   formula  fixed effects as in the brief + one random-effects term by participant;
  #            the clmm loop supports a random intercept only, (1 | participant)
  #   test     the coefficient the hypothesis rests on, named as R's model matrix
  #            names it (factor name followed by the level, e.g. devicetrackball)
  #   fixef    every fixed-effect coefficient, named, on the model's scale:
  #            lmer in the measure's units; glmer on the logit scale; clmm on the
  #            latent logit scale and WITHOUT an intercept (thresholds replace it)
  #   sd_participant   SDs of the random-effect terms, in the order the formula
  #            lists them (intercept first, then each slope)
  #   sigma    residual SD (lmer only)
  #   thresholds   the K-1 cut points of a K-category rating (clmm only)
  #   trials   observations per participant per condition for this model; defaults
  #            to trials_per_condition; 1 for a once-per-condition questionnaire rating
  models = list(
    list(
      dv = "movement_time",
      family = "lmer",
      formula = y ~ device + (1 + device | participant),
      test = "devicetrackball",
      fixef = c("(Intercept)" = 900, "devicetrackball" = 120),
      sd_participant = c(150, 60),
      sigma = 220
    ),
    list(
      dv = "error",
      family = "glmer",
      formula = y ~ device + (1 | participant),
      test = "devicetrackball",
      fixef = c("(Intercept)" = qlogis(0.05), "devicetrackball" = log(1.8)),
      sd_participant = c(0.5)
    ),
    list(
      dv = "rating",
      family = "clmm",
      formula = y ~ device + (1 | participant),
      test = "devicetrackball",
      fixef = c("devicetrackball" = -0.8),
      sd_participant = c(1.0),
      thresholds = c(-2, -0.7, 0.7, 2),
      trials = 1
    )
  )
)

## ---- END OF PARAMETERS ----

suppressPackageStartupMessages({
  library(lme4)
  library(lmerTest)
  library(ordinal)
  library(simr)
})
set.seed(params$seed)

# lme4 2.x moved nobars and findbars to the reformulas package and warns on
# every call through lme4; use reformulas when it is installed, lme4 otherwise.
.formula_tools <- if (requireNamespace("reformulas", quietly = TRUE)) {
  asNamespace("reformulas")
} else {
  asNamespace("lme4")
}
nobars <- get("nobars", .formula_tools)
findbars <- get("findbars", .formula_tools)

# One row per trial for n participants: the within factors crossed for every
# participant, the between factors assigned round-robin (participant 1 gets
# level 1, participant 2 level 2, ...) so that every prefix of the participant
# sequence, which is what powerCurve subsets, stays balanced.
make_design <- function(n, trials = params$trials_per_condition) {
  frame <- expand.grid(
    c(list(participant = factor(seq_len(n))),
      params$within,
      list(trial = seq_len(trials))),
    stringsAsFactors = TRUE
  )
  for (name in names(params$between)) {
    levels_b <- params$between[[name]]
    index <- ((as.integer(frame$participant) - 1L) %% length(levels_b)) + 1L
    frame[[name]] <- factor(levels_b[index], levels = levels_b)
  }
  frame
}

trials_of <- function(m) if (is.null(m$trials)) params$trials_per_condition else m$trials

fixed_formula <- function(formula) update(nobars(formula), NULL ~ .)

check_model <- function(m, frame, drop_intercept = FALSE) {
  columns <- colnames(model.matrix(fixed_formula(m$formula), frame))
  if (drop_intercept) columns <- setdiff(columns, "(Intercept)")
  if (!identical(columns, names(m$fixef))) {
    stop(m$dv, ": fixef must name exactly ", paste(columns, collapse = ", "),
         " in that order; got ", paste(names(m$fixef), collapse = ", "))
  }
  if (!(m$test %in% names(m$fixef))) {
    stop(m$dv, ": test ", m$test, " is not one of the fixef names")
  }
  bars <- findbars(m$formula)
  if (length(bars) != 1) {
    stop(m$dv, ": exactly one random-effects term, by participant, is supported")
  }
  re_columns <- ncol(model.matrix(reformulate(deparse(bars[[1]][[2]])), frame))
  if (length(m$sd_participant) != re_columns) {
    stop(m$dv, ": sd_participant needs ", re_columns,
         " value(s), one per random-effect column, in the formula's order")
  }
  if (m$family == "lmer" && is.null(m$sigma)) {
    stop(m$dv, ": sigma (the residual SD) is required for an lmer model")
  }
}

# lmer and glmer: build the model at the largest n and let simr refit it along
# the participant grid.
power_simr <- function(m) {
  frame <- make_design(max(params$n_grid), trials_of(m))
  check_model(m, frame)
  varcorr <- diag(m$sd_participant^2, nrow = length(m$sd_participant))
  model <- if (m$family == "lmer") {
    simr::makeLmer(m$formula, fixef = m$fixef, VarCorr = varcorr,
                   sigma = m$sigma, data = frame)
  } else {
    simr::makeGlmer(m$formula, family = binomial, fixef = m$fixef,
                    VarCorr = varcorr, data = frame)
  }
  method <- if (m$family == "lmer") "sa" else "z"  # Satterthwaite t; Wald z
  curve <- simr::powerCurve(model, test = simr::fixed(m$test, method),
                            along = "participant", breaks = params$n_grid,
                            nsim = params$n_sims, alpha = params$alpha,
                            progress = FALSE)
  s <- summary(curve)
  data.frame(dv = m$dv, n = s$nlevels, power = s$mean, lower = s$lower, upper = s$upper)
}

# clmm: simr cannot simulate it, so simulate the latent variable, cut it at
# the thresholds, fit ordinal::clmm and count the significant fits.
simulate_ordinal <- function(m, frame) {
  X <- model.matrix(fixed_formula(m$formula), frame)[, names(m$fixef), drop = FALSE]
  n <- nlevels(frame$participant)
  intercepts <- rnorm(n, 0, m$sd_participant[1])[as.integer(frame$participant)]
  latent <- as.vector(X %*% m$fixef) + intercepts + rlogis(nrow(frame))
  categories <- seq_len(length(m$thresholds) + 1)
  frame$y <- factor(cut(latent, c(-Inf, m$thresholds, Inf), labels = FALSE),
                    levels = categories, ordered = TRUE)
  frame
}

power_clmm <- function(m) {
  if (length(m$sd_participant) != 1L) {
    stop(m$dv, ": the clmm loop simulates a random intercept only; use (1 | participant)",
         " with one sd_participant value")
  }
  check_model(m, make_design(min(params$n_grid), trials_of(m)), drop_intercept = TRUE)
  rows <- lapply(params$n_grid, function(n) {
    hits <- 0L
    fits <- 0L
    for (i in seq_len(params$n_sims)) {
      frame <- simulate_ordinal(m, make_design(n, trials_of(m)))
      # A fit that errors, or whose covariance matrix is undefined (a NaN p,
      # common with one observation per participant per condition), is a
      # failed fit: excluded from the denominator, never counted as a miss.
      p <- tryCatch(
        suppressWarnings({
          fit <- ordinal::clmm(m$formula, data = frame, link = "logit")
          coef(summary(fit))[m$test, "Pr(>|z|)"]
        }),
        error = function(e) NA_real_
      )
      if (!is.finite(p)) next
      fits <- fits + 1L
      if (p < params$alpha) hits <- hits + 1L
    }
    failed <- params$n_sims - fits
    if (failed > 0L) {
      cat(sprintf("%s: %d of %d clmm fits failed at n = %d and were excluded\n",
                  m$dv, failed, params$n_sims, n))
    }
    if (fits == 0L) stop(m$dv, ": every clmm fit failed at n = ", n)
    interval <- binom.test(hits, fits)$conf.int
    data.frame(dv = m$dv, n = n, power = hits / fits,
               lower = interval[1], upper = interval[2])
  })
  do.call(rbind, rows)
}

results <- do.call(rbind, lapply(params$models, function(m) {
  if (m$family == "clmm") power_clmm(m) else power_simr(m)
}))

primary <- params$models[[1]]$dv
primary_rows <- results[results$dv == primary, ]
reached <- primary_rows$n[primary_rows$power >= params$target_power]
chosen <- if (length(reached) > 0) min(reached) else NA

cat(sprintf("\n## Power curve (%d simulations per point, alpha = %.3f, seed %d)\n\n",
            params$n_sims, params$alpha, params$seed))
cat("| Measure | n | Power | 95% CI |\n| --- | --- | --- | --- |\n")
for (i in seq_len(nrow(results))) {
  cat(sprintf("| %s | %d | %.2f | %.2f to %.2f |\n", results$dv[i], results$n[i],
              results$power[i], results$lower[i], results$upper[i]))
}
cat(sprintf("\nPrimary measure: %s\n", primary))
if (is.na(chosen)) {
  cat(sprintf(paste0("No participant count in the grid reaches power %.2f for the ",
                     "primary measure; extend n_grid or revisit the effect size, ",
                     "with a reason.\n"), params$target_power))
} else {
  cat(sprintf("Participant count: %d (the smallest grid value with power >= %.2f for %s)\n",
              chosen, params$target_power, primary))
  others <- results[results$n == chosen & results$dv != primary, ]
  for (i in seq_len(nrow(others))) {
    cat(sprintf("At n = %d, %s: power %.2f (%.2f to %.2f)\n", chosen, others$dv[i],
                others$power[i], others$lower[i], others$upper[i]))
  }
}
