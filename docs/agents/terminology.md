# Terminology reference

Use [CONTEXT.md](../../CONTEXT.md) for domain terms and avoided synonyms, and
[the ADRs](../adr/) for architectural decisions. This file only defines how to
choose names and records spellings or exceptions not owned by those sources.

## 1. Deviating from the standard term

Use the term selected by §2 unless one of these costs binds:

1. **Permanent surface mismatch** — with tool surfaces we don't control.
2. **Information loss** — the base term carries less structure than the concept
   needs.
3. **Semantic falsification** — the base term would make our records state
   something false.
4. **Collision/ambiguity** — the base term already means something else in our
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
  [ADR 0001](../adr/0001-vault-outlives-its-tools.md).
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
2. Verbatim machine-readable identifiers beat prose labels.
3. A versioned specification beats a living wiki, which beats a blog.

Determine scope before walking the tiers. A domain-specific authority governs
only its domain.

## 3. Recording a ruling

Record an adoption once, with its source, in the relevant §4 section. Record a
T8 coinage there with its local rule. Record a deviation once in the table
below, naming the declined anchor and §1 cost class. Put architectural rationale
in an ADR and term meanings in [CONTEXT.md](../../CONTEXT.md), then link to them
instead of restating them here. Two registers, and the declined anchor decides which a row enters: an OKF rule, section or field shape the vault does not meet registers in [okf-conformance.md](okf-conformance.md); a term's spelling or sense declined against an anchor registers in the table below. Both cite §1's cost classes.

| Governed spelling                                                                                   | Declined anchor                 | Cost                                                                                                                                                                                                                                            |
| --------------------------------------------------------------------------------------------------- | ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Pandoc `[@citation-key, locator]`                                                                   | OKF §5.1 footnote attribution   | 1 — permanent toolchain mismatch: the pinpoint locator has no home in OKF v0.2 and `sources[].id` stays the join key OKF expects                                                                                                                |
| `citation key` as the source's name; the Zotero item key qualified by the server id is its identity | OKF `sources`/`resource`        | Superseded 2026-09-07 by the ingest redesign spec §3.1, which mints the second identity the earlier row said was avoided. The `sources`/`resource` adoption stays deferred; the open cost is ongoing double-bookkeeping, not a lost distinction |
| Project `draft` / `parked` / `published` / `corrected` / `withdrawn`                                | OKF document lifecycle          | 2 — publication states would be lost                                                                                                                                                                                                            |
| `source` for the cited document; `venue` for its outlet                                             | OpenAlex `source` for an outlet | 4 — the senses collide; see [CONTEXT.md](../../CONTEXT.md#evidence-and-claims)                                                                                                                                                                  |

## 4. Governed spellings

### 4.1 Vault paths and note kinds

[CONTEXT.md](../../CONTEXT.md#vault) owns the standard vault paths and note names.
[okf-conformance.md](okf-conformance.md) owns the OKF-required root files
and frontmatter. This section adds only spellings not named there.

| Spelling                                              | Source or rule                                                                                        |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `projects/<name>/search-log.md`; `type: "search-log"` | PRISMA-S `search log`, scoped to a project                                                            |
| `system/`; `system/templates/`; `system/bases/`       | Product-owned vault tooling, kept outside the knowledge folders                                       |
| `fulltext/`                                           | Zotero's own `fulltext` naming (its sync preference and local-API endpoint), scoped to the text layer |
| `wiki/`                                               | The adopted compile tool's own page tree (T2 toolchain)                                               |

### 4.2 Claim and metadata language

Use the claim and verification terms in [CONTEXT.md](../../CONTEXT.md), the
verification record defined by
[ADR 0002](../adr/0002-verification-records-tell-the-truth.md), the transition
language in [ADR 0003](../adr/0003-deprecate-never-delete.md), the identity rule and the
bibliography authority in
[the ingest redesign spec](../superpowers/specs/2026-09-06-import-redesign-design.md)
(§3.1 and §3.2), which supersede the two suspended decision records that
previously held them.

| Spelling                                 | Source or rule                                                                                      |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `citationKey`                            | Zotero's own native field name (Zotero 8+), filled by Better BibTeX                                 |
| `zotero-server-id`                       | Prefixed to Zotero's own `Zotero-Server-ID` response header; qualifies the item key to one instance |
| `zotero-item-key`                        | Prefixed to Zotero's own item `key`, to disambiguate the frontmatter namespace                      |
| `zotero-item-version`                    | Prefixed to Zotero's own item `version`, to disambiguate the frontmatter namespace                  |
| `compile-input-sha256`                   | sha256 over the text-layer file capture wrote; the compile wrapper's input attestation              |
| `managed-sha256`                         | sha256 over the note body below the frontmatter                                                     |
| `[failed-verification:: <check>/<date>]` | Exact machine-written failure marker                                                                |
| `human:<identity>`                       | Human actor form; §4.5 defines the machine actor                                                    |

### 4.3 Commands and skill names

A new CLI command takes the first matching branch:

| Branch                         | Form                                                   | Current commands                                                                                                        |
| ------------------------------ | ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| Read-only report               | Bare report noun                                       | `doctor`, `inbox`, `probe`, `trust-tier`; `verify` is the established verb-form exception; `factcheck` remains one word |
| Ledger append                  | Record noun, or ledger name when no record noun exists | `finding`, `ack`, `search-log`                                                                                          |
| Persistent switch              | `arm-<gate>` / `disarm-<gate>`                         | `arm-publish`, `disarm-publish`                                                                                         |
| Lifecycle transition           | `mark-<status>`                                        | `mark-published`, `mark-corrected`, `mark-withdrawn`, `mark-parked`                                                     |
| Mechanical ingest step         | Bare imperative verb                                   | `capture`, `add`, `propagate`; `compile` is Part B's fourth                                                             |
| Other projection or derivation | Imperative verb-noun kebab                             | `stamp-type`; `scaffold` is the established single-verb exception                                                       |

Use kebab-case and exact [CONTEXT.md](../../CONTEXT.md) nouns. Do not invent
abbreviations, compatibility aliases, or multiple verbs for one act. Command
names do not persist in vault records and may be renamed outright.

Governed skill names are `setup-vault`, `project-flow`, `find-sources`,
`capture-source`, `verify-citations`, `factcheck-draft`, `publish`,
`evidence-conventions`, and `synthesis-conventions`.

### 4.4 Identifier inventory

Check ids, doctor probe ids, and reason codes are coined identifiers written to
durable surfaces. Use kebab-case. Update the appropriate row in the same change
that adds an identifier, and keep each registry on one physical Markdown table
row for the parity checks. Per-claim check values use
`<check>:<claim-link>:<target-kind>`, for example
`quote:<claim-link>:managed-region`. This table owns their spellings.

| Group            | Governed identifiers                                                                                                                                                                                                                                                                                                                                                                                  |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| check ids        | `citation-key`, `quote`, `update-notice`, `evidence-layer`, `identifier-discovery`, `disputed-claim`, `publish`, `factcheck`, `okf-frontmatter`, `okf-structure`, `tree`, `lifecycle`, `capture`, `propagation`, `captured-set`, `compile`                                                                                                                                                            |
| doctor probe ids | `tree`, `machine-config`, `zotero`, `write-guard`, `fulltext-sync`, `bbt`, `bbt-git`, `plugins`, `path-shim`, `translator-formats`, `compile-tool`, `remote`, `backup`                                                                                                                                                                                                                                |
| reason codes     | the `REASON_CODES` registry at HEAD: `budget-cap`, `contradiction`, `database-changed`, `deleted`, `disputed-claim`, `drift`, `fuzzy-quote`, `low-confidence`, `manual`, `matched`, `merged`, `mismatch`, `no-fulltext`, `no-identifier`, `not-admitted`, `not-captured`, `outage`, `re-keyed`, `recompile-needed`, `retracted`, `schema-violation`, `stale-key`, `trashed`, `unkeyed`, `warn-notice` |

Allowed register splits:

- `surface` means an enforcement point in `--surface` and
  `CLOSING_BY_SURFACE`; *tool surface* appears only in naming prose.
- `source` on `search-log` means the database or API searched, following
  PRISMA-S. It is distinct from [Source](../../CONTEXT.md#evidence-and-claims), the
  cited document.
- `ack` is the CLI's serialization of **Acknowledgment** (CONTEXT.md); `rw` is Retraction Watch's shorthand; `rv-` is the
  registered product prefix in §4.5.

### 4.5 Product identity

Name a product or supporting repository for the durable artifact it stewards;
if none exists, name the activity it serves. Qualify an ambiguous noun with its
field. Keep kind words such as `plugin` and `bundle` in the description, not the
name. Use kebab-case and no invented abbreviations.

`research-vault` follows the durable-artifact branch: `vault` is the artifact
defined in [CONTEXT.md](../../CONTEXT.md#vault) and protected by
[ADR 0001](../adr/0001-vault-outlives-its-tools.md); `research` disambiguates it.
The name of a researcher's own vault or repository is outside this ruling.

| Surface                                        | Governed spelling                                                                            |
| ---------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Repository slug; plugin and distribution names | `research-vault`                                                                             |
| Python module and CLI program                  | `research_vault`                                                                             |
| Process-written actor                          | `research_vault/<version>`                                                                   |
| Selector field                                 | `rv-selector`                                                                                |
| Vault tooling directory                        | `.research-vault/`                                                                           |
| Environment-variable family                    | `RV_*`                                                                                       |
| Internal scratch paths                         | `.research-vault-projection-`, `.research-vault-rollback`, `.research-vault-manifest-probe-` |

`rv` is the registered exception to the no-abbreviation rule for durable
markers and the environment-variable family. Keep a name family uniform. Use
the full product name on other surfaces, including the tooling directory and
scratch paths.

`harness` names the agent runtime only, never the product.

### 4.6 OKF adoption

Adoptions from OKF, recorded once per §3's rule (a vocabulary deviation is priced in the §3
table above, a conformance deviation in [okf-conformance.md](okf-conformance.md)'s
register; an adoption is named here, with its source):

| Adopted spelling                                                       | OKF source                                                                                                                          |
| ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `verified[].{by, at}`                                                  | OKF §5.2 event shape; `check` is the research-vault extension recording which check passed and driving coverage-derived trust tiers |
| `unverified` / `machine-confirmed` / `human-reviewed` trust tier names | OKF §5.3, verbatim                                                                                                                  |
| `human:<id>` / `<producer>/<version>` actor convention                 | OKF §7                                                                                                                              |

## 5. Retired spellings

A spelling the tree no longer uses. `tests/test_current_state.py::test_no_retired_vocabulary` reads this table — it is the deny-list's one writer — and refuses each pattern on every prose surface that states the present (dated records are out of scope). A row is a regular expression in a code span (`|` escaped as `\|`), the date it was retired, and what replaced it. The table's own rows are exempt from the scan; a prose line that names a retired spelling in order to forbid it uses one of the hatch words the test names (`_Avoid_`, `Declined anchor`, `stale names`, `not aliases`).

| Pattern                                      | Retired    | Replaced by                                               |
| -------------------------------------------- | ---------- | --------------------------------------------------------- |
| `\bliteratures/`                             | 2026-09-17 | `literature/` — "literature" is uncountable (#142)        |
| `synthesis/`                                 | 2026-09    | `wiki/`, written by the adopted compile tool              |
| `\bfixity-sha256\b`                          | 2026-09    | `managed-sha256`                                          |
| `knowledge-harness`                          | 2026-08    | `research-vault` (the product rename, #91)                |
| `\.harness/`                                 | 2026-08    | `.research-vault/`                                        |
| `\bHARNESS_`                                 | 2026-08    | `RV_*`                                                    |
| `\bhk-[a-z]`                                 | 2026-08    | `rv-` (the registered product prefix)                     |
| `\bmanaged region`                           | 2026-09    | the whole note body is capture's                          |
| `\bfree region`                              | 2026-09    | none — no hand-written region in a literature note        |
| `\b[Aa]dmission is (?:a\|the) human act`     | 2026-09    | selection is the person's act; `add` and `capture` follow |
| `\b[Aa]dmitted (?:through\|into\|to) Zotero` | 2026-09    | added to Zotero                                           |
| `\bcitekey:`                                 | 2026-09    | `citationKey:`                                            |
| `\bimport-source\b`                          | 2026-09    | `capture-source`                                          |
| `\bscreening-state\b`                        | 2026-09    | none — screening states retired with admission            |
| `\bLiterature screening states\b`            | 2026-09    | none                                                      |
| `\brename log\b`                             | 2026-09    | `system/propagations/` (the applied propagation plans)    |
