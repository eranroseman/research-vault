# Terminology reference

Use [CONTEXT.md](../CONTEXT.md) for domain terms and avoided synonyms, and
[the ADRs](adr/) for architectural decisions. This file only defines how to
choose names and records spellings or exceptions not owned by those sources.

## 1. Deviating from the standard term

Use the term selected by §2 unless one of these costs binds:

1. **Permanent surface mismatch** — with tool surfaces we don't control.
1. **Information loss** — the base term carries less structure than the concept
   needs.
1. **Semantic falsification** — the base term would make our records state
   something false.
1. **Collision/ambiguity** — the base term already means something else in our
   context.

For product names, class 4 also covers public-namespace collisions. Rename
effort, taste, sunk work, and precedent are not forcing costs.

Use one canonical term per concept. Add an alias only when an external contract
requires it. Preserve external API names verbatim at the boundary. A rename
updates every repository surface, including dated reports, transcripts, and
plans; git retains the earlier wording.

## 2. Precedence order for anchor sources

For the target surface, use the first applicable tier:

- **T1 — OKF**, within the structural scope set by
  [ADR 0001](adr/0001-vault-outlives-its-tools.md).
- **T2 — User-visible toolchain**: CSL first on bibliographic surfaces; then
  Zotero, BBT/ZotLit, Obsidian, Dataview, and Markdown.
- **T3 — Authorities of record**: Crossref, DataCite, DOI, W3C, CiTO/SPAR, and
  IETF.
- **T4 — Scholarly methods**: PRISMA/Cochrane/Covidence, GRADE, ICD 203/206,
  and plain scholarly English.
- **T5 — Cross-cutting aggregators**: OpenAlex, Wikidata, and scite.
- **T6 — Community conventions**: llm-wiki, Ideaverse/LYT, Ahrens/PKM,
  Appleton, GTD/PARA, and Wikipedia.
- **T7 — Developer tools**, on developer-facing surfaces only.
- **T8 — Author's coinage**.

Surface fit is absolute: discard any candidate that does not fit the target
surface. Among the remaining candidates within a tier, apply these tie-breakers
in order:

1. The vocabulary whose data we record beats one we merely resemble.
1. Verbatim machine-readable identifiers beat prose labels.
1. A versioned specification beats a living wiki, which beats a blog.

Determine scope before walking the tiers. A domain-specific authority governs
only its domain.

## 3. Recording a ruling

Record an adoption once, with its source, in the relevant §4 section. Record a
T8 coinage there with its local rule. Record a deviation once in the table
below, naming the declined anchor and §1 cost class. Put architectural rationale
in an ADR and term meanings in [CONTEXT.md](../CONTEXT.md), then link to them
instead of restating them here.

| Governed spelling                                                              | Declined anchor                 | Cost                                                                                                   |
| ------------------------------------------------------------------------------ | ------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Pandoc `[@citekey, locator]`                                                   | OKF footnote attribution        | 1 — permanent toolchain mismatch; [ADR 0001](adr/0001-vault-outlives-its-tools.md)                     |
| `citekey` as source identity                                                   | OKF `sources`/`resource`        | 1 — Better BibTeX and prose use the same address; [ADR 0004](adr/0004-citekey-is-the-only-identity.md) |
| `supports` / `disputes`                                                        | OKF untyped lineage             | 2 — stance would be lost; [ADR 0001](adr/0001-vault-outlives-its-tools.md)                             |
| Literature screening states in [CONTEXT.md](../CONTEXT.md#evidence-and-claims) | OKF document lifecycle          | 2 — screening is distinct from document maturity                                                       |
| Project `draft` / `parked` / `published` / `corrected` / `withdrawn`           | OKF document lifecycle          | 2 — publication states would be lost                                                                   |
| `source` for the cited document; `venue` for its outlet                        | OpenAlex `source` for an outlet | 4 — the senses collide; see [CONTEXT.md](../CONTEXT.md#evidence-and-claims)                            |
| `superseded` / `superseded-by`                                                 | OKF identity merge              | 3 — succession does not imply identity; [ADR 0003](adr/0003-deprecate-never-delete.md)                 |

## 4. Governed spellings

### 4.1 Vault paths and note kinds

[CONTEXT.md](../CONTEXT.md#vault) owns the standard vault paths and note names.
[ADR 0001](adr/0001-vault-outlives-its-tools.md) owns the OKF-required root files
and frontmatter. This section adds only spellings not named there.

| Spelling                                              | Source or rule                                                  |
| ----------------------------------------------------- | --------------------------------------------------------------- |
| `projects/<name>/search-log.md`; `type: "search-log"` | PRISMA-S `search log`, scoped to a project                      |
| `system/`; `system/templates/`; `system/bases/`       | Product-owned vault tooling, kept outside the knowledge folders |

### 4.2 Claim and metadata language

Use the claim and verification terms in [CONTEXT.md](../CONTEXT.md), the
verification record defined by
[ADR 0002](adr/0002-verification-records-tell-the-truth.md), the transition
language in [ADR 0003](adr/0003-deprecate-never-delete.md), the identity rule in
[ADR 0004](adr/0004-citekey-is-the-only-identity.md), and the bibliography
authority in
[ADR 0005](adr/0005-better-bibtex-owns-the-bibliography-export.md).

| Spelling                                 | Source or rule                                       |
| ---------------------------------------- | ---------------------------------------------------- |
| `fixity-sha256`                          | OAIS/NDSA `fixity`, with the algorithm made explicit |
| `managed-sha256`                         | Matching coined name for the managed-region witness  |
| `[failed-verification:: <check>/<date>]` | Exact machine-written failure marker                 |
| `human:<identity>`                       | Human actor form; §4.5 defines the machine actor     |

### 4.3 Commands and skill names

A new CLI command takes the first matching branch:

| Branch                         | Form                                                   | Current commands                                                                                                                     |
| ------------------------------ | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| Read-only report               | Bare report noun                                       | `doctor`, `inbox`, `probe`, `staleness`, `trust-tier`; `verify` is the established verb-form exception; `factcheck` remains one word |
| Ledger append                  | Record noun, or ledger name when no record noun exists | `finding`, `ack`, `search-log`                                                                                                       |
| Persistent switch              | `arm-<gate>` / `disarm-<gate>`                         | `arm-publish`, `disarm-publish`                                                                                                      |
| Lifecycle transition           | `mark-<status>`                                        | `mark-published`, `mark-corrected`, `mark-withdrawn`, `mark-parked`                                                                  |
| Other projection or derivation | Imperative verb-noun kebab                             | `import-note`, `backfill-selectors`, `archive-source`, `stamp-type`; `scaffold` is the established single-verb exception             |

Use kebab-case and exact [CONTEXT.md](../CONTEXT.md) nouns. Do not invent
abbreviations, compatibility aliases, or multiple verbs for one act. Command
names do not persist in vault records and may be renamed outright.

Governed skill names are `setup-vault`, `project-flow`, `find-sources`,
`import-source`, `verify-citations`, `factcheck-draft`, `publish`,
`evidence-conventions`, and `synthesis-conventions`.

### 4.4 Identifier inventory

Check ids, doctor probe ids, and reason codes are coined identifiers written to
durable surfaces. Use kebab-case. Update the appropriate row in the same change
that adds an identifier, and keep each registry on one physical Markdown table
row for the parity checks. Per-claim check values use
`<check>:<claim-link>:<target-kind>`, for example
`quote:<claim-link>:managed-region`. The
[foundation specification](superpowers/specs/2026-08-16-foundation-spec.md) owns
their behavior; this table owns their spellings.

| Group            | Governed identifiers                                                                                                                                                                                                                                                                                                      |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| check ids        | `citekey`, `doi`, `metadata`, `quote`, `update-notice`, `evidence-layer`, `identifier-discovery`, `web-archive`, `screening-state`, `disputed-claim`, `publish`, `factcheck`, `autoexport`, `render`, `integrate`, `okf-frontmatter`, `okf-structure`, `tree`                                                             |
| doctor probe ids | `tree`, `machine-config`, `zotero`, `bbt`, `autoexport`, `staleness`, `remote`, `backup`, `inbox`, `okf`                                                                                                                                                                                                                  |
| reason codes     | the `REASON_CODES` registry at HEAD: `budget-cap`, `contradiction`, `disputed-claim`, `drift`, `fuzzy-quote`, `low-confidence`, `manual`, `matched`, `mismatch`, `missing-archive`, `no-identifier`, `not-admitted`, `not-imported`, `outage`, `retracted`, `schema-violation`, `stale`, `superseded-note`, `warn-notice` |

Allowed register splits:

- `surface` means an enforcement point in `--surface` and
  `CLOSING_BY_SURFACE`; *tool surface* appears only in naming prose.
- `source` on `search-log` means the database or API searched, following
  PRISMA-S. It is distinct from [Source](../CONTEXT.md#evidence-and-claims), the
  cited document.
- `ack` is the foundation specification's serialization of
  **Acknowledgment**; `rw` is Retraction Watch's shorthand; `rv-` is the
  registered product prefix in §4.5.

### 4.5 Product identity

Name a product or supporting repository for the durable artifact it stewards;
if none exists, name the activity it serves. Qualify an ambiguous noun with its
field. Keep kind words such as `plugin` and `bundle` in the description, not the
name. Use kebab-case and no invented abbreviations.

`research-vault` follows the durable-artifact branch: `vault` is the artifact
defined in [CONTEXT.md](../CONTEXT.md#vault) and protected by
[ADR 0001](adr/0001-vault-outlives-its-tools.md); `research` disambiguates it.
The name of a researcher's own vault or repository is outside this ruling.

| Surface                                        | Governed spelling                                                                            |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Repository slug; plugin and distribution names | `research-vault`                                                                             |
| Python module and CLI program                  | `research_vault`                                                                             |
| Process-written actor                          | `research_vault/<version>`                                                                   |
| Vault markers and selector field               | `%%rv-managed%%`, `%%/rv-managed%%`, `rv-selector`                                           |
| Vault tooling directory                        | `.research-vault/`                                                                           |
| Environment-variable family                    | `RV_*`                                                                                       |
| Internal scratch paths                         | `.research-vault-projection-`, `.research-vault-rollback`, `.research-vault-manifest-probe-` |

`rv` is the registered exception to the no-abbreviation rule for durable
markers and the environment-variable family. Keep a name family uniform. Use
the full product name on other surfaces, including the tooling directory and
scratch paths.

`knowledge-harness`, product uses of `harness`, `.harness/`, `HARNESS_*`, `hk-`,
and `.harness-*` are stale names from the unfinished rename, not aliases.
`harness` remains the name of the agent runtime only.
