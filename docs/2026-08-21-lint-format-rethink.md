# Rethink audit: vault and repo lint and formatting

Date: 2026-08-21. Method: `/rethink-audit` rungs; prior art dispatched to a research agent against primary sources. Subject: the lint/format architecture accumulated across Plan Q's amendments (the one-form-owner matrix) plus the vault's canonical-form machinery. Verdict: **vault half already sound — keep, now with named precedent; repo half needs one structural change** (a single orchestration seam) that closes a requirement the accreted design silently violated.

## requires (evidence-tagged)

R1 one form-owner per file type, zero remembered rules (`docs`, author-ruled across four push-backs) · R2 vault dialect: sole writer is the formatter; external formatters excluded (`docs` + measured: mdformat and mdformat-obsidian both escape wikilinks/inline fields) · R3 correctness lints are a separate axis from form (`docs`) · R4 pin-exact; canonical form must not drift across tool versions (`docs`) · R5 no new toolchains where avoidable (`docs`: oxfmt, taplo rejections) · R6 no network at check time (implicit in the pinning posture; made explicit here) · R7 **one command locally == CI** (surfaced by this audit; the accreted design violated it) · R8 vault lints warn-tier, deterministic-only closure (`adr`/`docs`) · R9 history: content never rewritten, form canonicalized once (`docs`) · R10 boundaries mechanically enforced (`docs`/`tests`).

Callers: CI workflow; local dev (author, Codex, subagents); vault-side: pre-commit *template*, doctor, hooks (separate system — note the name collision with the repo's dev-lane pre-commit). External consumers: scaffolded vaults. Unreached: pre-commit.ci SaaS, future MCP surfaces.

## prior-art (research-agent findings, primary sources)

- **"The emitting program is the formatter" is established practice with our exact caveat**: Go's `go/format.Source` exists so generators emit canonical form directly, and its docs warn byte-stable output requires a pinned formatter — the ecosystem already learned "the pin is a render-contract component". Rust `prettyplease` (pretty-printer for generated code, chosen over shelling to rustfmt) and Jest's snapshot writer are the same policy. Vault-side design independently validated.
- **Golden files: freeze, never format** (Jest `.snap` reviewed-not-edited; insta's fixed serialization; pandas/pip exclude test-data trees from all hooks). Matches tests-track-system-output.
- **Anti-drift is a specific convention**: pre-commit config as single source (`pre-commit run --all-files` locally == CI — pip, pandas, ruff's own repo, Scientific Python guide), and/or pip's layer: CI yaml reduced to the one target developers type. They compose.
- **Enabler**: pre-commit `repo: local` + `language: system` hooks run tools from the existing pinned venv — pure orchestration, no second env layer, no network, pip-installable. Multiplexer alternatives each break constraints: treefmt (Go binary, formatters-only), trunk (proprietary launcher, downloads), MegaLinter (Docker), dprint (network-fetched plugins, own formatters).
- Precedent for stage-tiering slow/binary hooks: ruff's repo runs actionlint as a manual-stage hook.

## design

1. **Vault half: unchanged.** Parser-as-lint, sole-writer-as-formatter, canonicality property tests, warn-tier surfacing.
2. **Repo half: one orchestration seam.** `.pre-commit-config.yaml` of `repo: local` / `language: system` hooks only, over the pinned venv: ruff format+check, mypy, mdformat, yamlfix, pyproject-fmt, config-validity (JSON canonical + skill frontmatter via the suite). File routing and the `core/tests/` exclusion are declarative config. One command — `pre-commit run --all-files` — is the entire local and CI form/lint invocation. Quality metrics (CRAP, drywall, mutation gate) stay separate workflow steps: different axis. Residuals as manual-stage hooks, run CI-side: actionlint, shfmt, shellcheck (Go/binary tools R5 declines to require locally). Matrix's durable home: the config itself + README dev section. IDE alignment: committed `.vscode/settings.json` so the editor never fights the owners (format-on-save only for Python via the same ruff; prettier disabled — the original corruption incident came from IDE prettier).

## gap

Commands duplicated between workflow yaml and local docs (drift by construction — R7 violation, accident of accretion) · shfmt CI-action-only (same) · excludes imperative in path lists (works; declarative is the target) · everything else already matches (owners, pins, measured rejections, JSON-canonical-in-test, frontmatter contract test). `.vscode/settings.json` is JSONC — a dialect surface owned by VS Code, outside the `json.tool` owner (same class as `.base` files).

## migrate

1. Pin `pre-commit==4.6.2` into the dev extra; author `.pre-commit-config.yaml` (local/system hooks, excludes, manual-stage residuals).
2. Plan Q Task 5: collapse form/lint workflow steps into venv install + `pre-commit run --all-files --show-diff-on-failure` + `pre-commit run --all-files --hook-stage manual` (residuals); keep CRAP/drywall/mutation steps.
3. Replace local verify block and README dev section with the one command; matrix table to config comments + README.
4. Commit `.vscode/settings.json` + `.vscode/extensions.json` (ruff recommended); document the pre-commit name collision (repo dev lane vs vault trust gate) in the config header.

## trade-offs

- Framework dep for orchestration, used as a dumb router (no remote repos, no env building, no network). Flips if it misbehaves solo → fallback is pip's other half: a make/nox target wrapping the same commands, one-file swap.
- Residuals stay CI-side (actionlint, shfmt, shellcheck) — R7 holds everywhere except three binaries. Flips if local runs wanted → `prek` (single Rust binary, same config) or pinned binary downloads.
- Name collision with the vault's pre-commit — documentation cost only.
