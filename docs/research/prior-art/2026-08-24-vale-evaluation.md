# Vale as a prose linter for the research-vault repo and the vault — declined

Disposition: historical (2026-09-06) [should-be-scoping-review]

**Verdict (author-ruled 2026-08-24): declined.** The terminology guard is adopted instead as a pytest that parses `CONTEXT.md` at test time — no generated artifact, so registry drift is structurally impossible (the eliminate rung, per AGENTS.md). Vale would be mechanism-plus-guard. **Revisit triggers, and only these: a demand for editor integration (LSP squiggles for a human author), or a vault-side user request.** The user-side answer that never touches trust machinery is the [Obsidian Vale plugin](https://github.com/ChrisChinchilla/obsidian-vale) — a reader installs it in their own vault, and research-vault knows nothing about it. **A third surface, user-facing documentation, was measured the same day and adds a third trigger; see §8.**

This note exists so nobody re-runs the evaluation from scratch. The measured yields are the decision; the configuration knowledge in §4 is the part a future evaluator would otherwise have to rediscover by experiment.

Method: Vale v3.18.0 (Linux 64-bit release binary) unpacked to `/tmp`, driven with scratch configs in `/tmp/valetest`, run against this repo's 248 markdown files and against synthetic vault notes written to the real claim syntax of `skills/evidence-conventions/SKILL.md`. Nothing was written into the repo. Doc facts below are from `https://docs.vale.sh/llms-full.txt` (fetched 2026-08-24; note `vale.sh/docs/*` 301s to `docs.vale.sh/*`) and are marked where they were confirmed empirically.

## 1. What Vale is

A Go binary, MIT-licensed, read-only: it reports and never rewrites. Rules are YAML files extending one of twelve checks (`existence`, `substitution`, `occurrence`, `repetition`, `consistency`, `conditional`, `capitalization`, `metric`, `readability`, `spelling`, `sequence`, `script`), grouped into styles under a `StylesPath`. A `Vocab` folder holds `accept.txt` and `reject.txt`, one regex per line; `reject.txt` entries feed a built-in `Vale.Avoid` existence rule, `accept.txt` entries feed `Vale.Terms` (which enforces exact casing) and are added to every style's exception list.

The read-only property matters for the vault: Vale does not violate the "formatters are writers too" contract in `research_vault/templates/vault/AGENTS.md`. That contract is not what rules it out — §5 is.

## 2. Measured yield — terminology

A `reject.txt` of 25 unambiguous terms lifted from `CONTEXT.md`'s `_Avoid_` lines, run over `docs/`, the root markdown files, and `skills/`:

| Surface                                                            | `Vale.Avoid` hits                                 |
| ------------------------------------------------------------------ | ------------------------------------------------- |
| `skills/`                                                          | 0                                                 |
| `AGENTS.md`, `README.md`                                           | 0                                                 |
| `docs/adr/0004-citekey-is-the-only-identity.md`                    | 1 — "claim address" (canonical: **claim link**)   |
| `docs/product-landscape/2026-08-22-product-comparison-verified.md` | 5 — three "claim address", two "confidence level" |

Six hits outside the two glossaries, of which roughly three or four are genuinely actionable — the two "confidence level" hits describe *other products'* epistemics and are arguably legitimate usage. Across 248 files. The most agent-facing prose in the repo, `skills/`, was clean.

The ADR hit was real drift against our own glossary and was fixed in the same commit as this note.

## 3. Measured yield — spelling: unusable, do not enable

`Vale.Spelling` over `docs/` plus the root markdown files: **1434 alerts across 22 files, 317 distinct tokens, effectively 100% false positive.** Top tokens: `Zotero` (131), `medsci` (117), `Memoria` (68), `citekey` (54), `frontmatter` (43), `Crossref` (38), then a long tail of citekeys (`pedrohcgs`, `gbrain`, `nvk`, `cookjohn`) and author surnames (`Zhao`, `Pratiyush`).

The structural objection, not just the count: **citekeys are unbounded and grow with the library.** A vocabulary is a fixed list; the corpus of citekeys is whatever Zotero admits next. No `accept.txt` maintenance regime keeps up. In the vault this is worse — every literature note filename is a citekey.

## 4. Configuration knowledge worth keeping

Each item below was confirmed by running the binary, not read off the docs.

**Glossary self-flagging is the first thing that breaks.** `CONTEXT.md` and `research_vault/templates/vault/system/glossary.md` *define* the rejected terms, so `Vale.Avoid` fires on every `_Avoid_:` line — 28 alerts on `CONTEXT.md` alone. The fix that works:

```ini
BlockIgnores = (_Avoid_:[^\n]+)
```

Confirmed: 28 alerts to 0. The alternative fallback, if a `BlockIgnores` form ever stops working, is a per-file section (`[CONTEXT.md]` with `Vale.Avoid = NO`) — a glossary is a definition site, so losing Avoid coverage there costs nothing.

**`BlockIgnores` does *not* reach front matter.** `(?s)(\A---\n.*?\n---\n)` was tested and the citekey in `citekey: "nvkTrial"` was still flagged. Front matter is parsed into per-field `text.frontmatter.<field>` scopes before block ignores apply, and there is no documented blanket switch to exempt it. For a vault whose front matter is entirely machine-owned, this has no clean answer — the practical answer is not to run spelling there at all.

**`BlockIgnores` *does* reach managed regions.** This form works:

```ini
BlockIgnores = (?s)(%%rv-managed%%.*?%%/rv-managed%%)
```

Confirmed: a synthetic literature note with `Teh`, `Zhao`, and `bioRxiv` inside its managed region went silent under it. Necessary, not optional — a finding inside a managed region cannot be acted on, because the bridge regenerates the region and a hand edit raises a drift finding.

**`SkippedScopes` is a *core* option, not a format-specific one.** Putting it under a `[*.md]` section is a hard error:

```
E100 [NewE201] Runtime error
'SkippedScopes' is a core option; it should be defined above any syntax-specific options (`[...]`).
```

It must sit in the global section, which means a single config cannot skip blockquotes in the vault while keeping them in dev docs. Two configs, or two runs.

**The global config is always loaded, and read last.** Vale loads `$XDG_CONFIG_HOME/vale/.vale.ini` (Unix) *in addition to* the project config, after it, so multi-valued keys merge and single-valued keys are overridden by whatever a contributor has on their machine. Local and CI results diverge silently. **Any invocation in a hermetic lane must pass `--no-global`.** Every run recorded in this note used it.

**Only `error` sets a non-zero exit code.** Exit `0` = clean, `1` = findings, `2` = runtime error. The `1`/`2` split is the same distinction our four-state model draws between UNMATCHED and UNREACHABLE (see `trust-gates-prior-art.md` §3), so an integration path exists if one is ever needed: `2` maps to UNREACHABLE, `1` to a finding.

**Two behaviours are correct out of the box and are the only real discriminators against a grep.** Both confirmed with a targeted probe file:

- Code spans are skipped. `` `gh issue list --state open` `` in `docs/agents/issue-tracker.md:9` fires under a naive grep and is silent under Vale.
- `Vale.Avoid` applies word boundaries. "no synthesis claim addresses this part" in `skills/project/SKILL.md:56` fires under a naive grep and is silent under Vale; "the claim address is stable" fires correctly.

A naive grep over the same term list returned 21 hits across 9 files, most of them these two false-positive classes.

**Vault syntax that Vale already handles correctly** (no configuration needed): inline `[@citekey, locator]` citations are not spell-checked, including digit-free citekeys such as `kepanoObsidian` and `vanDerBergSmit`; `^c-anchor` block anchors are not flagged; `%%` markers are not flagged; hyphenated and slashed wikilink targets (`[[llmwiki-taxonomy]]`, `[[swarmvault/overview|the overview]]`) are skipped. **Bare single-token wikilinks are flagged** — `[[llmwiki]]` and `[[gbrain]]` both alerted.

**Install and network.** Vale is a Go binary, not pinnable in the venv beside ruff/mypy/mdformat. The repo already has a slot for that shape — shellcheck and shfmt run as `stages: [manual]` with CI executing them. A PyPI `vale` package exists but was **not** verified; it may fetch the binary post-install, which would matter for the offline-at-check-time contract. Vale itself needs no network if you write your style locally and set no `Packages` key; `vale sync` is only for downloading packages. If a package is ever added, pin the release URL rather than the name — naming a package installs its latest release.

**Append-only paths must be globbed out of any adoption.** `research/`, `analysis/`, and `docs/adr/` are frozen by the `record-immutability` hook. A finding there cannot be fixed *and cannot even be annotated away* — you cannot edit a frozen ADR to add a `<!-- vale off -->`. Worth recording the converse: commit-time linting would have caught the ADR 0004 "claim address" *before* it froze, which is an argument for diff-scoped linting if this is ever revisited.

## 5. Why the vault is the harder no

Three hazards, in ascending order of seriousness:

1. **Front matter cannot be exempted** (§4). Machine-owned fields get flagged with no clean suppression.
2. **Managed regions need `BlockIgnores`** (§4). Solvable, but it is configuration that must not be forgotten.
3. **Blockquotes must be skipped, or the tool becomes an active hazard.** A synthetic quote claim carrying `exhibted` and `attrision` inside its `> blockquote` was flagged by Vale as two spelling errors. That text is *verbatim source*, byte-checked by quote verification. An agent that "fixes" a Vale spelling alert there breaks the check the vault exists to run. Flagging verbatim quoted text as misspelled is an induce-the-agent-to-break-byte-verification failure — the worst class this system has. It is preventable (`SkippedScopes = ..., blockquote`, which was confirmed to work), but it is preventable only by remembering to prevent it, and §4 shows that key cannot be set per-format.

Beyond the hazards: the vault is a *user's* private repo scaffolded by `setup-vault`. Adopting Vale there means shipping a binary install step to every reader and adapting its output into the four-state model, the review queue, and the acknowledgment machinery — a second check engine beside `lints.py`, for a yield §2 measures as three or four findings per 248 files.

## 6. Why the pytest wins on the rung ordering

AGENTS.md orders fixes: eliminate the problem > add a mechanism > add a rule. The three candidates sat on different rungs.

- **Pytest parsing `CONTEXT.md` at test time — eliminate.** No generated artifact exists, so there is no seam for drift to open at. The glossary is the registry, read live.
- **Vale with a generated `reject.txt` — mechanism plus guard.** A generator, a generated file, and a consistency test watching the seam between them. Three moving parts to keep one list true.
- **Vale with `reject.txt` as the registry — never live.** It inverts authority: the meaning layer becomes a render of a linter's config file.

The yield math does not rescue the mechanism rung. Three or four actionable findings across 248 files, and the two genuine discriminators — code-span skipping and word-boundary anchoring — are about five regex lines inside the pytest (strip spans, `\b`-anchor the terms). Editor LSP is the one feature that cannot be reproduced, and the drift-writers here are agents, who do not read squiggles. Against that: a Go binary outside the venv pin model, the `--no-global` silent-divergence trap, and the two-config blockquote hazard if it ever nears the vault.

The `_Avoid_` format-tightening cost is real but hits every option equally — comma-splitting the lines today breaks on parentheticals such as `import (that is the projection step that follows)` and `"source" for an outlet — that is a **venue**`. The pytest can dodge most of it with a paren-aware comma split; a generator cannot dodge it at all.

## 7. The lineage close

Vale was already in this project's design lineage before this evaluation. `docs/research/prior-art/trust-gates-prior-art.md` §3 records its three-tier severity model and its exit-code split as precedent for our own four-state result model, and `docs/terminology.md` T7 names "Vale severities" as an anchor source for dev-facing surfaces.

The project took the idea and, on evidence, declines the tool.

## 8. Addendum (2026-08-24) — user-facing documentation, the third surface

Asked after the ruling: does the verdict change for prose written for a *reader* rather than for an agent? It does not, and the measurement is worth keeping because the failure mode is different from §2's and §5's.

**There is barely a corpus.** Strict user-facing — what a reader of this project actually reads — is `README.md` (165 words) plus the vault templates shipped into every reader's vault (1,062 words): **roughly 1,200 words.** The CLI contributes nothing; `research_vault/__main__.py` has one `help=` string and no help prose. The number reaches 11.4k words only by folding in `skills/*/SKILL.md`, which `docs/terminology.md` T7 already classifies as dev-facing rather than vault prose — a different surface with a different ruled vocabulary.

**Method.** Unlike §2–§5, this run used real style packages: `Packages = Microsoft, Google`, synced over the network into a scratch `StylesPath` (`vale sync` worked first try; the package route is not the friction point). Run over `README.md`, the vault templates, and the nine `SKILL.md` files — 14 files, ~11.4k words. **Caveat on every count below: both styles were loaded at once and they duplicate heavily** — the acronym rules fired 50 times each on identical spots. A real deployment picks one style, so the raw counts roughly halve. The percentage does not move.

**1414 alerts (575 error, 109 warning, 730 suggestion). 87% of them — 1239 — are house-voice conflicts:**

| Rule                                 | Hits | What it demands                 |
| ------------------------------------ | ---- | ------------------------------- |
| `Microsoft.Dashes` + `Google.EmDash` | 427  | stop spacing em dashes          |
| `Contractions` (both styles)         | 238  | "don't" over "do not"           |
| `Semicolon` / `Semicolons`           | 164  | "try to simplify this sentence" |
| `Passive` (both styles)              | 124  | flags `'is admitted'`           |
| `Google.Parens`                      | 123  | "use parentheses judiciously"   |
| `Microsoft.SentenceLength`           | 54   | keep sentences under 30 words   |

Spaced em dashes, semicolons, parentheticals, formal non-contracted phrasing, and long sentences are this project's deliberate register, in prose whose whole purpose is normative precision. The remaining 175 alerts are 57% duplicate pairs across the two styles, leaving roughly 125 distinct.

**The durable finding is an authority conflict, and it holds at any corpus size.** `docs/terminology.md` §2 sets a ruled eight-tier precedence order for naming. A third-party style package arrives as an unranked ninth authority that outranks nothing and objects loudest:

- `Google.WordList` demands "command-line tool" instead of **CLI** — T7 names CLI vocabulary as an anchor source.
- `Microsoft.Terms` prefers "specification" over **spec** — the repo ships `docs/superpowers/specs/`.
- `Microsoft.Passive` flags `is admitted` — **admission** is a defined glossary term and that is its precise conjugation.
- `Microsoft.Vocab` and `Google.WordListCase` fire *on glossary definition lines*, telling the naming authority to rename itself.

This is not noise to be tuned away. It is a second naming authority installed beside the one the project spent its terminology pass ruling.

**True positives, in full:** `PKM` unexpanded in `README.md` line 3, defined nowhere a reader reaches — real, and fixed in commit `3244371` by spelling it out rather than glossing it (used once, it earns no abbreviation). `Google.Timeless` on "currently" in the vault glossary (2 hits) — arguably real for prose meant to outlive a version. `TOML` flagged as an undefined acronym — false, it is standard in a developer section. **Yield: one to three findings across ~11.4k words**, obtainable by reading a 165-word README once.

**Neither existing trigger fires.** "User-facing" changes the *reader*, not the *writer*. Vale sits in the authoring pipeline, and the writers here are still agents — the same fact that sank the LSP argument in §6. A human reading the output does not put a human at the keyboard.

**New revisit trigger, added by this addendum:** *a genuine user-docs corpus gets authored* — a documentation site, a getting-started guide, anything on the order of thousands of words written for readers. At that point the reasons change shape: acronym first-use expansion and readability become the case for the tool, terminology is already covered by the pytest, and the §4 configuration knowledge and the authority conflict recorded here are what that evaluation should start from rather than rediscover.
