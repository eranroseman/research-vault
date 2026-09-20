# OKF conformance

The vault outlives its tools by conforming to the Open Knowledge Format (OKF, [GoogleCloudPlatform/open-knowledge-format](https://github.com/GoogleCloudPlatform/open-knowledge-format)). The decision is [ADR 0001](../adr/0001-vault-outlives-its-tools.md); this file is the mechanism — what OKF requires, how the vault discharges it, and where it deviates. The pin (the OKF commit and the `SPEC.md` digest the vault targets) has one writer, `.github/okf-pin.json`, read by the weekly `okf-spec-drift` job in `.github/workflows/quality.yml`; a bare version number was rejected because v0.2 was amended in place the day after adoption, and nothing noticed.

## The rules

OKF §11's three rules, verbatim — paraphrase is what drifted before they were copied:

1. Every non-reserved `.md` file in the tree contains a parseable YAML frontmatter block.
2. Every frontmatter block contains a non-empty `type` field.
3. Every reserved filename (`index.md`, `log.md`) follows the structure in §8 and §9 respectively when present.

OKF §3.1 fixes reserved-ness to `index.md` and `log.md` alone. The vault adds one rule of its own on top: a note's `type` is derived from its folder (`literature/` → `literature`, `log/` → `daily`, `inbox/` → `fleeting`, `projects/<name>/draft.md` → `project`), so a type that contradicts its folder is a finding.

## Adopted families

Beyond §11, the vault adopts OKF's optional families wherever adoption is additive, since OKF §4.1 permits producer keys alongside OKF's reserved ones: the actor prefixes `human:<id>` and `<producer>/<version>` (OKF §7), the trust tier names `unverified` / `machine-confirmed` / `human-reviewed` (OKF §5.3), and the `verified[].{by, at}` event shape (OKF §5.2). The adopted spellings are recorded in [terminology.md](terminology.md) §4.6. Adopting a family means the vault carries a second spelling of data it already holds — the price of a consumer needing no research-vault knowledge to read the bundle.

## How conformance is discharged

By code and a pin, not by intention:

- `research_vault/structure.py` — `check_note_frontmatter` (rules 1 and 2 and the folder-type rule), `check_reserved` (rule 3) and `check_tree`; every `verify` run reports them under the check ids `okf-frontmatter`, `okf-structure` and `tree`, and the commit and publish surfaces close on all three.
- `research_vault/stamp.py` — the fixer half of rule 2: stamps a derivable `type` on a file that lacks one, at capture, at publish and through `stamp-type`.
- `research_vault/okf.py` — regenerates `log.md` in OKF §9's shape.
- doctor's `tree` probe repairs the scaffold before observing it.
- The weekly `okf-spec-drift` job compares upstream `SPEC.md` against the pin and opens an issue on a mismatch. Reconciling it is the work: read the diff, decide adopt or deviate (a new row below), move the pin deliberately — `ref`, `sha256`, `method` and `measured` in `.github/okf-pin.json`, whose shape `tests/test_config_validity.py` asserts.

## Deviation register

A conformance deviation is an OKF rule, section or field shape the vault does not meet, priced with [terminology.md](terminology.md) §1's cost classes: 1 permanent surface mismatch, 2 information loss, 3 semantic falsification, 4 collision. The declined anchor decides the register: an OKF rule, section or field shape registers here; a term's spelling or sense declined against an anchor is a vocabulary deviation and registers in terminology.md §3.

| Deviation                                                                  | Declined anchor                                         | Cost                                                                                                                                                                                                                                                                                                |
| -------------------------------------------------------------------------- | ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Frontmatter on `wiki/index.md`, written by the adopted compile tool        | OKF §8 (index files carry no frontmatter)               | 1 — permanent mismatch with a tool whose index path is hard-coded and whose own lint requires the frontmatter OKF forbids; the deviation is one file in a machine-owned tree, and a consumer that ignores unknown frontmatter reads it correctly (`research_vault/structure.py`, `_EXEMPT_INDEXES`) |
| Untyped `inbox/` fleeting captures at creation                             | OKF §11 rule 1 (frontmatter on every non-reserved file) | 1 — permanent mismatch with the capture-time editor, the uncontrolled surface; `stamp-type` converges frontmatter at triage; the ADR protects the record, not the airlock                                                                                                                           |
| `supports` / `disputes` stance links (frozen pending the workflow audit)   | OKF untyped lineage                                     | 2 — stance would be lost                                                                                                                                                                                                                                                                            |
| No vault-owned freshness field; `refresh_due` on the compile tool's ledger | OKF §5.5 `stale_after`                                  | Not a deviation — the concept is kept, in one system. OKF's absolute instant and the tool's `refresh_due` are the same field under two names; the vault writes neither and reads the ledger's. `verify --as-of` supplies the comparison's other operand (ingest spec §3.2, §7)                      |
| `verified[].check` field and coverage-derived trust tiers                  | OKF §5.2 `{by, at}` event shape                         | 3 — collapsing to `{by, at}` alone would lose which check passed, the tier-coverage derivation it drives                                                                                                                                                                                            |
| `verified[].at` as a calendar date                                         | OKF §5 ISO 8601 datetime with UTC offset                | 3 — recorded pending an ADR 0002 reconciliation; [ADR 0002](../adr/0002-verification-records-tell-the-truth.md)'s no-padded-precision rule vs the genuinely date-valued upstreams                                                                                                                   |
| `[[citation-key#^claim-id]]` claim and stance links (frozen)               | OKF §6.1 markdown link form                             | 1 — the Dataview inline-field grammar requires the wikilink form; a markdown link's `]` would close the field early                                                                                                                                                                                 |
| No adoption of OKF §10 Attested Computation                                | OKF §10 Attested Computation                            | Declined — `managed-sha256` and the bibliography byte-comparison can't be attested consumer-side; they remain tool-only computations                                                                                                                                                                |
