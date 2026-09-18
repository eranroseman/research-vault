# OKF v0.2 conformance audit

Disposition: historical (2026-09-06)

Tiers 0–2 + Tier 5 landed 2026-09-02, plan `docs/superpowers/plans/2026-09-02-okf-conformance.md`.

Audited 2026-09-01 against the Open Knowledge Format v0.2 specification as published at
`GoogleCloudPlatform/open-knowledge-format@ad30107` (`SPEC.md`, 37748 bytes, last amended
2026-08-21). Method: eight per-section finder agents over the enumerated writer surfaces,
then one adversarial verifier per finding required to re-derive both the spec quote and the
`file:line` evidence independently. 83 findings raised, 65 survived, 18 refuted; the survivors
are deduplicated across dimensions into the items below.

Every item below carries a spec clause and a repo location. Nothing here is applied; this is
a review. `docs/terminology.md` carries uncommitted working-tree changes from a parallel
session and was not touched. Corrections applied 2026-09-01 after an independent review of this
report; git history holds the superseded text.

## Verdict

The vault is **not** a conformant OKF v0.2 bundle, and the gap is smaller than it looks. Three
findings fail §11's numbered bundle-conformance rules; one more fails an enumerated consumer
MUST and one a consumer SHOULD — the tool reading a vault, not the vault's own files. All five
are mechanical and none
costs the vault any semantics to fix. Everything else is either a reserved-key collision the repo's
own naming rules already forbid, an optional family left unadopted, or documentation that
misdescribes the spec.

The root cause is single and documentary: [ADR 0001](../adr/0001-vault-outlives-its-tools.md)
restates OKF's conformance rules from memory rather than quoting §11, and every structural
violation below traces to that paraphrase. The doctor `okf` probe then implements the
paraphrase, so it reports `OKF artifacts conformant` over a vault that is not.

| Bucket                    | Count | Meaning                                                                          |
| ------------------------- | ----- | -------------------------------------------------------------------------------- |
| Rule violation            | 5     | Fails OKF v0.2 §11 — three bundle rules, one consumer MUST, one consumer SHOULD. |
| Namespace collision       | 3     | An OKF-reserved key carries foreign values.                                      |
| Unadopted optional family | 6     | Conformant, but the spirit gap.                                                  |
| Documentation defect      | 12    | The repo misdescribes the spec it conforms to.                                   |
| Confirmed conformant      | 10    | Worth keeping and worth recording.                                               |

## 1. Rule violations

§1.1–§1.3 fail §11's numbered rules, which is what defeats ADR 0001's bundle-conformance claim.
§1.4 fails a consumer MUST §11 enumerates by name; §1.5 fails the consumer SHOULD beside it
("SHOULD derive trust tiers and staleness only from the fields specified here"). Both are the
tool misreading a conformant vault rather than writing a nonconformant one.

### 1.1 Bundle-root `index.md` carries a `type` key the spec does not permit

§8: "Index files contain no frontmatter, with one exception: a bundle-root `index.md` MAY
carry an `okf_version` key (§12)." §12 closes the exception: "(the only place frontmatter is
permitted in an `index.md`)". The grant is one key, not an extension point — §4.1's
"Producers MAY include any additional keys" governs *concept* documents, and §3.1 removes
`index.md` from that class.

`research_vault/templates/vault/index.md:1-4` ships:

```yaml
---
type: "index"
okf_version: "0.2"
---
```

Worse, the probe mandates it. `research_vault/scaffold.py:360-362` raises
`index.md: type must be "index"`, and `tests/test_okf.py:96-101` writes the *spec-conformant*
form and asserts `Result.UNMATCHED`. The tool would reject a conformant vault.

**Fix (lossless).** Delete line 2 of the template; delete the `index_type` branch at
`scaffold.py:360-362` and replace it with a check that rejects any root-index key other than
`okf_version`; invert `tests/test_okf.py:96-101`, `tests/test_templates.py:68,83`, and
`tests/test_scaffold.py:87`; drop the claim from
`docs/superpowers/specs/2026-08-16-foundation-spec.md:16,25`. Nothing reads the root index
`type` except the probe that demands it.

### 1.2 Regenerated root `log.md` is not a §9 log

§9: "The format is a flat list of date-grouped entries, newest first". "Date headings MUST use
ISO 8601 `YYYY-MM-DD` form." §11 rule 3 binds this: "Every reserved filename (`index.md`,
`log.md`) follows the structure in §8 and §9 respectively when present."

`research_vault/okf.py:22-38` is the sole writer. `day_files = sorted(...)` is ascending;
`tail = lines[-tail_entries:]` preserves that order; the body is `# Log`, then a flattened
tail, then `## Days` over `[[log/<stem>]]` wikilinks. Running it produces no `## YYYY-MM-DD`
heading at all — the only second-level heading is the non-date `## Days`, entries are
flattened out of their day files so each line keeps only its `HH:MM` and loses its date, and
the order is oldest-first. Compare the spec's own reference bundle,
`bundles/acme_retail/log.md`, which is date-grouped and newest-first.

`scaffold.py:369-370` checks only that the file exists. Rule 3 is never evaluated anywhere in
the codebase. The file is rewritten on every import and every publish (`publish.py:411`,
`__main__.py:301`, `scaffold.py:221`), so the violation is written continuously while the
probe reports MATCHED.

**Fix (lossless).** Key `_day_lines` output by day file, emit `## <stem>` headings in reverse
chronological order, keep or fold in the `## Days` index. No entry text is lost. Frontmatter
on `log.md` is fine — the reference bundle has it, and §8's prohibition names `index.md` only.

### 1.3 Fleeting `inbox/` notes are frontmatter-free concept documents

§11 rule 1: "Every non-reserved `.md` file in the tree contains a parseable YAML frontmatter
block." §3.1 fixes reserved-ness to `index.md` and `log.md` — "All other `.md` files are
concept documents." Authorship is not a criterion.

`research_vault/scaffold.py:337` excludes the whole surface:
`if relative.startswith("inbox/") and relative != "inbox/review-queue.md": continue`, and
`tests/test_okf.py:73` pins the blindness. This is not a human-only surface:
`skills/evidence-conventions/SKILL.md:12` directs the *agent* to write these files and gives
no frontmatter instruction.

**Ruled, 2026-09-02: split by author, with the exemption carried by rationale rather than
silence.** Agent-written fleeting notes adopt `type: "fleeting"` at write — one line in
`evidence-conventions`, free, closing the machine-written half of this finding. Human quick
capture stays frontmatter-free at creation; the type arrives mechanically at triage, by a
linter that stamps `type: "fleeting"` onto untyped `inbox/` notes. The stamp prepends only
where no frontmatter exists — a note whose head is YAML-shaped junk gets reported, not edited,
because converting a readable note into a parse error is the one way the stamp can do harm.
`inbox/review-queue.md` is tool-managed, carries frontmatter, and conforms regardless; the
exemption does not license it to degrade.

What remains is honest nonconformance, recorded: while an unstamped capture exists, the bundle
fails §11 rule 1. The rationale is scope plus workflow. `inbox/` holds knowledge *candidates* —
by the vault's own Iron Law, prose ahead of its evidence is not yet knowledge — and `system/`
holds machinery; both are part of the vault, neither is part of the knowledge record ADR 0001's
guarantee protects. An OKF consumer that skips an untyped fleeting note loses no knowledge, so
the exemption sits outside the guarantee rather than denting it (`system/` needs no exemption
today — its files already carry frontmatter). The workflow half is the accepted bound's
practical leg, untouched by D2's refutation of its spec leg: forcing metadata syntax on quick
capture fails in practice. OKF has no way to mark a subtree as outside the bundle, which is why
this must be an exemption rather than a boundary declaration — and why a bundle-scope marker is
a second upstream filing candidate beside §9.5's locator issue: every real vault has an
airlock, and a spec that binds the whole tree forces this same choice on all of them. Register:
one `docs/terminology.md` §1 row carrying this rationale; probe: the success string names the
exemption instead of claiming blanket conformance.

### 1.4 A bare `verified` mapping is treated as malformed

§11 enumerates this as a consumer MUST: "MUST treat a bare `verified` mapping as a one-element
list (§5.2)."

`research_vault/events.py:59-66` does the opposite — a non-`list` value returns
`([], malformed=True)`. Verified live: a note carrying the spec's own example,
`verified: {by: "human:eran", at: "2026-08-02T09:00:00Z"}`, returns `unverified` from
`events.trust_tier`, `[]` from `verified_checks`, and makes `record_pass` raise. The parser
handles the mapping fine (`frontmatter.py:33` `_INLINE_DICT`); the rejection is semantic.

**Fix.** Normalize before validating: `raw_events = [raw_events] if isinstance(raw_events, dict) else raw_events`.

### 1.5 `_valid_event` requires a foreign key, so one spec-shaped entry poisons the list

`research_vault/events.py:35-42` uses set equality: `set(event) == {"by", "at", "check"}`. An
OKF-shaped `{by, at}` entry — the exact shape §5.2 defines — is therefore invalid, and via
`events.py:62-66` marks the *entire* `verified` collection malformed. `verify.py:800-820`
wraps `record_pass` in a blanket `except ... ValueError: pass`, so every subsequent
deterministic pass on that note is dropped with no event, no error, and no finding — the note
silently stops accumulating trust.

The governing clause is §11's consumer SHOULD, not a MUST: "SHOULD derive trust tiers and
staleness only from the fields specified here." §5.2's `{by, at}` shape is what the vault
refuses to derive from. The publish gate is *not* in the harm chain — `_publish` runs a fresh
`verify_state` and reads `surface_decision`, never the stored events (`publish.py:352-364`) —
so the failure is silent trust loss, not a mysterious gate hold. `record_pass` on the project
note at `publish.py:368` would raise rather than block, which is a different and louder
failure.

**Fix (four parts, all additive on the write path).**

1. `_verified_events`: normalize a bare mapping (item 1.4).
2. `_valid_event`: accept `{"by", "at"} <= set(event)`, and accept either a calendar date or
   an offset-bearing ISO 8601 datetime for `at`. Relaxing only the key set is not enough —
   `_calendar_date` at `events.py:26-32` still rejects `2026-06-25T09:00:00Z`.
3. `trust_tier`: keep check-less foreign events in the list so `events.py:287`'s `human:`
   test sees them, but exclude them from the `checks` coverage set. ADR 0002's
   "emptiness is not a pass" and MATCHED-only minting are untouched — only the reader becomes
   tolerant; `record_pass` keeps writing `{by, at, check}`.
4. Add the `docs/terminology.md` §3 row that records the `check` extension and the
   coverage-based tier derivation as a deviation from §5.3, at cost class 3.

## 2. Namespace collisions

These are conformant under §11 but violate the repo's own governance:
`docs/terminology.md` §1 class 4 exists for exactly this case, and OKF's key names are the
T1 anchor. Declining a family's *values* does not license squatting its *key*.

### 2.1 `status` carries two foreign value spaces

§5.4 defines `status: draft | stable | deprecated`, with "Absent `status` ⇒ `stable`."

The vault writes screening states (`unscreened`/`included`/`excluded`/`superseded`,
`templates/vault/system/templates/literature.md:7`, `CONTEXT.md:74`) and project publication
states (`draft`/`parked`/`published`/`corrected`/`withdrawn`, `publish.py:206`) into that same
key. `docs/terminology.md:69-70` frames both as declining "OKF document lifecycle" at cost
class 2. That is the wrong frame: nothing is *lost* by carrying both, so class 2 does not
bind; what is happening is class 4, and the table's own rule then requires the vault's field
to be renamed.

**Fix, and it is not free.** Rename to `screening-state` (a CONTEXT.md name) and a governed
publication-state spelling (`publication-status` is *not* yet one — terminology.md §4 would have
to rule it), freeing `status` to carry a real §5.4 value. But this is a breaking migration, not
an additive one: `lints.py:430` `lint_published_drift` keys on the project note's `status`
through `_project_status` (`lints.py:340-375`) and compares the working tree against the
published tag, so a rename either fires drift on every published project or silently removes the
watch. Design the migration through the drift lint before touching the key — the collision is
real and so is the cost of vacating it.

### 2.2 `verified[].at` is a calendar date, not an ISO 8601 datetime

§5: "Every timestamp-valued key in OKF is an ISO 8601 datetime with an explicit UTC offset,
for example `2026-06-30T14:00:00Z`."

`events.py:26-32` requires `YYYY-MM-DD` and `events.py:102-104` writes it. Actual bytes:
`verified:\n  - {by: "research_vault/0.1.0", at: "2026-09-01", check: "doi"}`. Note the
contrast with `generated.at`, which `literature_notes.py:213-220` renders correctly as Z-suffixed ISO —
so the vault already knows how.

This is a §5 producer SHOULD, not a §11 MUST, so the cheap disposition is a recorded
deviation citing ADR 0002's no-padded-precision rule and the genuinely date-valued upstreams
(`verify.py:950-951`, `publish.py:_publication_stamp`). Widening the predicate is the better
answer but changes stored bytes and needs an ADR 0002 reconciliation first.

**This is the reconciliation obligation ADR 0001 accepted, already fired and missed.** The
timestamp rule entered the spec in commit `ad30107` on 2026-08-21 — one day after ADR 0001
was accepted — without a version bump.

### 2.3 Shipped templates put unsubstituted placeholders into `generated`

`templates/vault/system/templates/project.md:5`, `synthesis.md:5`, and `literature.md:8` ship
`generated: {by: "{{ACTOR}}", at: "{{NOW}}"}`. In the code and tests the strings appear
elsewhere only in two assertions that pin them (`tests/test_templates.py:159,165`, which any
fix must update); a research note under `docs/research/validation-slice/` quotes them
incidentally. No Python and no skill step substitutes them, and `scaffold.py:216` copies them
verbatim into every scaffolded vault.

`skills/project-flow/SKILL.md:48` makes this concrete: project notes are authored prose, "no
CLI verb is involved", so the agent either carries the literal placeholder into durable
frontmatter or invents an actor — the exact case §7 makes a producer MUST. A §5.2 consumer
reading `generated.at` gets an unparseable literal.

**Fix.** Either delete the line (§5: "All are optional. Their absence carries meaning" — but
this contradicts `foundation-spec.md:61-62`, which requires generation metadata, so the spec
needs the matching amendment), or have the skills write
`generated: {by: "human:<id>", at: "<generated_at_now()>"}`, reusing `literature_notes.py:213`.

## 3. Unadopted optional families

All conformant. Each needs a disposition — adoption or a recorded declination — because
`docs/terminology.md` §3 requires one and silence currently stands in for both.

| Family                        | Status                           | Recommendation                                                                                                                                                                                                                                                                                                                                                                                               |
| ----------------------------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `resource` (§4.1)             | Never written                    | **Adopt.** Literature notes already carry `doi`/`url` (`literature_notes.py:229-236`); `resource: https://doi.org/…` names the paper, not the note. Not universally free: §5.1 makes `resource` REQUIRED within a `sources` entry, and a DOI-less source (a book, an ISO standard) needs a resolvable URL or one of §5.1's scope descriptors instead.                                                        |
| `sources` (§5.1)              | Never written                    | **Adopt.** `sources: [{id: <citekey>, resource: <doi-url>, title: …}]` from data in hand. `resource` is REQUIRED within an entry, so the DOI must carry — the citekey alone is not enough.                                                                                                                                                                                                                   |
| `title`, `description` (§4.1) | Never written                    | **Adopt.** Both values are already in hand at render time; `description` feeds §8 index entries and search snippets.                                                                                                                                                                                                                                                                                         |
| `tags` (§4.1)                 | Never written                    | Assess. Obsidian tags exist; whether they belong in OKF `tags` is a modelling call.                                                                                                                                                                                                                                                                                                                          |
| `stale_after` (§5.5)          | Declared pass-through, no writer | Decide: wire it to the `staleness` probe, or drop the pass-through claim.                                                                                                                                                                                                                                                                                                                                    |
| Attested Computation (§10)    | Wholly unadopted                 | **Record the declination.** Not required by §11, and `fixity-sha256` / the bibliography byte-comparison genuinely cannot be attested consumer-side. But two candidates are real: `managed-sha256` and the quote check are sanctioned computations whose definitions live only in the tool, not the bundle. Also note `trust_tier` folds per-run state into the doc-level tier §10.6 defines as verification. |

### 3.1 The `sources`/`resource` declination rests on a claim the spec does not make

`docs/terminology.md:67` declines `sources`/`resource` because "the citekey is source
identity" ([ADR 0004](../adr/0004-citekey-is-the-only-identity.md)). ADR 0004's argument is
about minting a second *identity*; neither field is one. §2 makes the Concept ID the file
path with `.md` removed — here `literature/<citekey>` (`literature_notes.py:129`), so the citekey is the
Concept ID's leaf, not the whole of it — and §5.1's `id` is
"a stable key used to attribute individual claims", precisely the slot the citekey fills.
§4.1's `resource` names the underlying asset, i.e. the paper.

So the vault does not decline OKF identity; **it already implements it**. Adopting `resource`
and `sources` requires no second identity, touches no citekey, and breaks no contract with
Better BibTeX, pandoc, or Obsidian. Class 1 does not bind. The row should be split: keep a
footnote-attribution row (class 1, real — see below), and either delete the `sources` row or
re-record it with an honest cost, which is maintenance, not one of §1's four classes.

### 3.2 Machine-written navigation links are invisible to any OKF consumer

§6.1 supports two link forms, both standard markdown. Every navigation link the tool writes is
an Obsidian wikilink: `templates/vault/index.md:7-12` and `okf.py:35`. A grep for `](` across
`research_vault/templates/vault/` returns no vault-content markdown link at all. The cost is
§8 progressive disclosure — an OKF consumer opening the bundle root gets zero traversable
entry points.

**Fix (free).** `- [literature/](literature/) — …` and
`f"- [{day_file.stem}](log/{day_file.stem}.md)"`. Relative links are §6.1's second supported
form and are natively clickable in Obsidian; nothing is lost.

**Do not convert claim and stance links.** `[[citekey#^claim-id]]` cannot become a markdown
link: `claims.py:13-14` documents the wikilink-specific inline-field grammar, and a markdown
link's `]` closes a Dataview inline field early. This is conformant (§6.1 is MAY; §11 does not
constrain link form) but currently unrecorded — it needs a `docs/terminology.md` §3 row, cost
class 1.

### 3.3 The footnote-attribution declination is correct, and there is no seam to revisit it

§5.1's per-claim footnotes keyed to `sources[].id` genuinely conflict with pandoc
`[@citekey, locator]`; `docs/terminology.md:66` prices it correctly at class 1. The usual
escape — emit OKF footnotes at an export boundary while the living vault stays pandoc — is not
available: `publish.py` publishes in place via git tags and status writes; there is no bundle
projection and no pandoc render step anywhere in the codebase. (The `render` check id is *not*
that seam and is not free to take: it is a live import-side hold class for render rejections,
wired 2026-08-22 and test-pinned at `tests/test_cli_live.py:1502,1538`. Reusing it would be the
same class-4 collision this report condemns in §2.1.) Building a projection seam is the only
path to adopting §5.1 without touching the toolchain, and it is a larger piece of work than
anything else in this report.

## 4. Documentation defects

Five of the twelve are in one paragraph. `docs/adr/0001-vault-outlives-its-tools.md:7`
restates §11 from memory; three of its misstatements licensed the structural violations above
(D1–D3), and the other two mislead without licensing anything (D4 overstates two sound
deviations, D5 is the missed reconciliation).

| #   | Defect                                                                                                                                                                                                                                                                                                                                                                                                                  | Consequence                                                                                                        |
| --- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| D1  | "every machine-written `.md` carries parseable YAML frontmatter" — §11 rule 1 says "Every non-reserved `.md` file in the tree", scoped by reserved-ness, not authorship.                                                                                                                                                                                                                                                | Licensed §1.3.                                                                                                     |
| D2  | "OKF instructs consumers to tolerate nonconforming files." No basis. §11's tolerance list is scoped to "all other constraints" — every bullet names something that was never nonconformance (missing optional fields, unknown types, unknown keys, broken links, missing `index.md`). Nothing in the spec tolerates a missing frontmatter block.                                                                        | The false warrant under §1.3. Propagated to `foundation-spec.md:16` and quoted into code at `scaffold.py:326-329`. |
| D3  | States OKF's §8/§9/§12 MAYs as OKF "rules": "root `index.md` declares the OKF version and lists the vault tree; root `log.md` is a machine-regenerated summary…". Silently drops §8's no-frontmatter rule and §9's date-grouped format.                                                                                                                                                                                 | Licensed §1.1 and §1.2.                                                                                            |
| D4  | "OKF's rules are structural only" and "adopting OKF's words would buy no additional interop" — false against §5.3, §7, and §11's consumer contract. The vault has *already banked* that interop: `CONTEXT.md:91` uses §5.3's three tier names verbatim, and `AGENT_ACTOR` follows §7.                                                                                                                                   | Overstates the case for two deviations that are individually sound.                                                |
| D5  | "Conformance is version-tracking (v0.2 at adoption)" with no commit pin. v0.2 is amended in place: `ad30107`, "Make every timestamp an ISO 8601 datetime with an explicit offset", 2026-08-21, one day after the ADR. §12 still says 0.2 and §13.2 lists no timestamp change.                                                                                                                                           | §2.2 is the missed reconciliation.                                                                                 |
| D6  | The reconciliation obligation ADR 0001:17 calls "the mechanism's substance" has no implementation: no CI job (`quality.yml` has none), no pin, no checksum, and `scaffold.py:363-365` accepts any non-empty `okf_version` string.                                                                                                                                                                                       | Nothing would notice the next amendment either.                                                                    |
| D7  | `foundation-spec.md:16` bolds "**The vault is a structurally conformant OKF v0.2 bundle**" and in the same sentence states the fact that defeats it. Same overclaim at `CONTEXT.md:9`.                                                                                                                                                                                                                                  | Status claim not supportable until §1 is closed.                                                                   |
| D8  | `docs/terminology.md:72` declines "OKF identity merge" — a construct v0.2 does not contain and §13.2 shows v0.1 did not either. With no OKF assertion to falsify, the recorded class-3 cost cannot bind. The nearest real construct is §5.4 `deprecated`, which ADR 0003 already matches semantically.                                                                                                                  | Phantom row; misleads later readers into pricing a deviation that does not exist.                                  |
| D9  | `docs/terminology.md:67` declines `sources`/`resource` on an identity ground the spec does not make (§3.1 above).                                                                                                                                                                                                                                                                                                       | Blocks a free adoption.                                                                                            |
| D10 | The uncommitted `docs/terminology.md` rewrite dropped every OKF adoption row while §3 line 58 still mandates "Record an adoption once, with its source". Specifically now recorded nowhere: which of `{by, at, check}` is OKF §5.2 and which is the research-vault extension; §5.3 as the source of the tier names; §7 as the source of the actor convention (line 102 attributes `human:<identity>` to internal §4.5). | The naming authority no longer records its own T1 anchoring.                                                       |
| D11 | `skills/synthesis-conventions/SKILL.md` never mentions frontmatter, `type: "synthesis"`, or `system/templates/synthesis.md`. Contrast `project-flow/SKILL.md:48`, which does route through its template.                                                                                                                                                                                                                | A skill-following agent can write a §11-nonconformant note.                                                        |

And one code-level documentation defect: `_okf_probe` (`scaffold.py:342-374`) returns
`"OKF artifacts conformant"` while checking only rule 2 over a subset. Rule 3 is never
evaluated. The reserved-name test at line 335 is asymmetric — `path.name == "index.md"`
matches at any depth (correct per §3.1) but `relative == "log.md"` matches only at the root,
so a nested `projects/x/log.md`, which §9 explicitly permits ("A `log.md` file MAY appear at
any level of the hierarchy"), would be flagged missing-type. The probe is also warn-only
(`__main__.py:46`), so nothing blocks a commit or a publish.

## 5. Confirmed conformant

Worth stating, and worth recording in `docs/terminology.md` §4 where D10 removed it.

- **`generated`** is written exactly per §5.2 and §5: required `by`, and `at` as a Z-suffixed
  ISO 8601 datetime (`literature_notes.py:213-220`).
- **§7 actor convention** followed exactly by every code-written record —
  `research_vault/<version>` and `human:<id>`.
- **§5.3 trust tiers** — `unverified` / `machine-confirmed` / `human-reviewed`, the spec's
  three names verbatim, derived rather than stored.
- **§12 `okf_version`** declared with the exact key, value form, and location.
- **Nested `index.md`** correctly frontmatter-free, and test-pinned.
- **Rule 2** holds on every non-reserved concept document, mechanically enforced.
- **The citekey is the leaf of the OKF Concept ID** — §2's "path of the concept's file within
  the bundle, with the `.md` suffix removed" resolves to `literature/<citekey>`. The vault
  implements OKF identity rather than declining it.
- **No §10 key or the `Attested Computation` type name is squatted.**
- **Broken links never fail the probe**, matching §6.1's tolerance requirement.
- Synthesis notes use §5.4's value set verbatim (`draft`).

## 6. Checked and cleared

Three finder agents reported ADR 0001's spec pointer
(`github.com/GoogleCloudPlatform/knowledge-catalog`, `okf/SPEC.md`) as stale. **It is not.**
Verified 2026-09-01: the URL returns HTTP 200, and the file is byte-identical to
`open-knowledge-format/SPEC.md` (both 37748 bytes, `diff` clean). The spec now also has its
own dedicated repository, and the ADR's pointer named a mirror inside a product repo — worth
updating for clarity, but it resolved. (Updated after this audit, in `9f30b5b`/`3338502`; the
paragraph above evaluates the pre-fix text.) The only real gap is the missing commit pin (D5).

Also cleared: non-adoption of §10 is not a §11 violation; claim-link wikilinks are conformant;
`references/` (§6.3) is explicitly "a naming convention, not a requirement".

## 7. Path to 100%

Ordered by the repo's own maxim — eliminate the problem, then add a mechanism, then a rule,
then prose. Tiers 0–2 close every §11 violation, rule 1 modulo §1.3's recorded exemption: an
unstamped human capture in `inbox/` is nonconformant until the triage stamp lands on it.

**Tier 0 — producer fixes, no semantics lost.**

1. Delete `type: "index"` from the root index template (§1.1).
2. Emit date-grouped, newest-first `log.md` (§1.2).
3. Convert the two machine-written navigation surfaces to relative markdown links (§3.2).
4. Substitute or delete the `{{ACTOR}}`/`{{NOW}}` placeholders (§2.3).
5. Fleeting `inbox/` notes, per §1.3's ruling: `evidence-conventions` types agent-written
   captures at write; the triage stamp linter converges human captures; the register row and
   honest probe string record the residual exemption.

**Tier 1 — make the probe the mechanism, so this audit never has to run again by hand.**

1. Rewrite `_okf_probe` against §11 verbatim: rule 1 as a check distinct from rule 2; rule 3
   asserting §8 (no frontmatter in a nested index, at most `okf_version` at the root) and §9
   (date-form headings, newest-first); reserved-name matching by `path.name in {"index.md", "log.md"}` at any depth.
2. Narrow the success string to what was actually verified.
3. Pin the spec: record `open-knowledge-format@<sha>` plus a `SPEC.md` checksum, and have the
   probe or a scheduled CI job re-fetch and diff, opening an issue on mismatch. This is the
   reconciliation obligation ADR 0001 already accepted (D6).
4. Decide whether `okf` stays in `DOCTOR_WARN_ONLY`. A conformance claim the ADR calls
   load-bearing, enforced only by a warning, is the state that let five violations ship.

**Tier 2 — reader tolerance in `events.py`** (§1.4, §1.5). ADR 0002 untouched, but the write
path is *not* untouched and the naive version corrupts notes: `_replace_frontmatter_list` finds
its insertion point by matching a line equal to `verified:`
(`events.py:_replace_frontmatter_list`), which a bare mapping's `verified: {by: …, at: …}` line
does not match. Normalize the reader without teaching the writer to recognize the bare form and
the next `record_pass` appends a second `verified:` block beside the first. The bare-mapping
branch has to be handled in both directions or not at all.

**Tier 3 — vacate the reserved key** (§2.1). A breaking migration, not an additive rename:
design it through `lint_published_drift` first, and the publication-state spelling needs a
terminology ruling before it exists. Optionally dual-emit a real §5.4 `status` once vacated.

**Tier 4 — additive adoption**: `resource`, `sources`, `title`, `description` (§3).

**Tier 5 — record what remains.** Correct ADR 0001's four misstatements (D1–D4); pin its spec
reference (D5); retract or qualify the conformance claims in `foundation-spec.md:16` and
`CONTEXT.md:9` until Tier 0–2 lands (D7); delete the phantom `identity merge` row and split the
`sources`/`resource` row (D8, D9); restore the OKF adoption block §3 mandates (D10); add the
missing deviation rows — claim-link syntax, the `check` extension and coverage-based tier
derivation, `verified[].at` precision, and the §10 declination; add the frontmatter sentence
to `synthesis-conventions` (D11).

Everything else on the current deviation table either does not need to be a deviation or does
not correspond to anything in the spec. What survives Tier 4 is the register's to count —
Tier 5's rows, with per-claim attribution the load-bearing one — see §8.1.

## 8. Proposed ADR 0001

### 8.1 What "100% compliant, in rules and in spirit" can honestly claim

**Rules.** All three §11 rules hold once Tier 0 lands — rule 1 modulo §1.3's recorded
exemption for untyped human captures awaiting the triage stamp — and Tier 1 makes them hold
*mechanically* rather than by assertion: a probe written against §11's text, closing rather
than warn-only, over a pinned spec hash. That is the whole of rule-level conformance; §11
requires nothing else of a bundle.

**Spirit.** Three claims, each checkable:

1. *No OKF-reserved key carries a value OKF would misread.* Tier 3 vacates `status`; Tier 2
   makes the `verified` reader accept the spec's own shapes; Tier 0 removes the `generated`
   placeholders. §2.2's `verified[].at` precision survives as a recorded deviation until the
   ADR 0002 reconciliation widens the predicate.
2. *Every optional family has a recorded disposition.* Tier 4 adopts the four additive families
   (`resource`, `sources`, `title`, `description`); Tier 5 records the rest — `stale_after`,
   `tags`, and §10 — as adoptions or priced declinations. Silence, which is the current state
   for most of them, is not a disposition.
3. *The two remaining "deviations" are supersets of OKF, not refusals of it.* §6.1 says the
   kind of a relationship "is conveyed by the surrounding prose, not by the link itself" — the
   vault conveys it in a Dataview field beside the link, which is more than OKF asks for and
   contradicts nothing it says. And OKF has no sub-document addressing at all, so
   `[[citekey#^claim-id]]` extends into empty space rather than declining a construct.

That leaves exactly one genuine residual: per-claim attribution renders as pandoc
`[@citekey, locator]` rather than a `[^citekey]` footnote. Once `sources` is adopted with
`id: <citekey>` (Tier 4), literature notes become self-describing — but that does *not* close
the source half, because §5.1's join is document-scoped: the footnote label resolves into the
same document's `sources` list, and the citations live in `synthesis/` and `projects/` notes
that Tier 4 never touches. The *pinpoint* half does not close either, and cannot: OKF v0.2 has
no locator concept anywhere. §9 decomposes the residual and gives the ways to close each half.

### 8.2 The proposed replacement text

Adopt after Tiers 0–5 land, not before; the claims it makes — the mechanism, and the register's
dispositions — are only true once both exist. Substitute the real values for `<sha>` and
confirm the hash at adoption time. The
deviation and adoption registers stay in `docs/terminology.md` §3/§4 — this ADR states the
principle and points there, per that file's own "record it once" rule.

```markdown
# The vault outlives its tools

Status: accepted (2026-08-20)

The vault is the researcher's permanent record; research-vault is one tool that operates on
it. The decision: **the vault must remain fully usable — readable, navigable, and adoptable by
other tools — if research-vault disappears.** The vault is therefore plain markdown + YAML
frontmatter in a git repository, with no runtime dependency on research-vault, and its
survivability guarantee is carried by a named external mechanism rather than by
research-vault-private convention.

**Current mechanism: conformance with OKF** (Open Knowledge Format — spec:
[GoogleCloudPlatform/open-knowledge-format `SPEC.md`](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md)),
which was growing an ecosystem of agent-facing knowledge tools at adoption. **Conformance is
pinned, not merely versioned**: the vault targets OKF v0.2 as published at
`open-knowledge-format@ad30107`, `SPEC.md` sha256
`26aa5da029278939f914e578107242d9607d4f2dc5fe153272b82f9ed1030101`. The pin exists because
v0.2 has already been amended in place without a version bump, so a bare version number is not
an anchor.

§11's three rules are reproduced verbatim rather than paraphrased, because the paraphrase is
what drifted:

1. Every non-reserved `.md` file in the tree contains a parseable YAML frontmatter block.
2. Every frontmatter block contains a non-empty `type` field.
3. Every reserved filename (`index.md`, `log.md`) follows the structure in §8 and §9
   respectively when present.

§3.1 fixes reserved-ness to `index.md` and `log.md` alone, so authorship is not a criterion.
One exemption is recorded: `inbox/` holds knowledge candidates, not knowledge — human quick
capture may sit untyped until the triage stamp adds `type: "fleeting"`, because the record this
ADR protects does not include the airlock, and forcing metadata syntax on quick capture fails
in practice. Agent-written captures are typed at write; the exemption's register row prices the
residual. Rule 3 pulls in §8
— a nested `index.md` carries no frontmatter, and the bundle root carries `okf_version` and
nothing else — and §9 — a `log.md`, at the root or any level below it, is date-grouped under
`## YYYY-MM-DD` headings, newest first. The doctor `okf` probe asserts all three against this text and re-checks the pinned
hash, so neither a drifting vault nor a drifting spec passes unnoticed. **The probe is the
mechanism; this ADR is only its rationale.**

**Conformance is structural and semantic.** OKF's optional families define a consumer contract
on top of §11's structure — §7's actor prefixes, §5.3's trust tiers, §5.4's lifecycle values —
and the vault adopts each one wherever adoption is additive, because §4.1 admits producer keys
and §11 forbids consumers rejecting them, so the vault's own schema rides alongside OKF's
rather than inside its reserved names. No OKF-reserved key carries a value OKF would misread.
Every family carries a disposition — adopted or declined with a cost class — recorded once in
[docs/terminology.md](../terminology.md); silence is not a disposition.

The deviations that survive that rule are recorded there, not here. The load-bearing one is
per-claim attribution: it renders as pandoc `[@citekey, locator]` rather than §5.1's `[^id]`
footnote, a permanent mismatch with a toolchain the vault does not control (cost class 1). It is
a rendering difference over the same join — `sources[].id` is the citekey, and §5.1 directs
consumers to resolve attribution "through the matching entry, not by parsing the footnote prose"
— except for the pinpoint, which OKF v0.2 has no way to carry at all.

**Scope bound:** the vault preserves the *record*, not the evidence artifacts. PDFs and
snapshots live in Zotero storage, outside the git boundary — git is not the blob store — so
artifact recoverability is delegated to the user's Zotero sync/backup, with doctor's persistent
warning as the only compensating control. At solo scope this is a stated boundary, not a
compliance control.

## Considered Options

Mechanism alternatives, all rejected: **no named mechanism** — rely on markdown + git being
inherently portable (rejected: portable bytes are not an adoptable structure; a successor tool
would inherit files but no contract for navigating them). **Export-boundary-only projection** —
emit a conformant bundle only when publishing (rejected: insures published output, not the
living vault). **Structural conformance without OKF's vocabulary** (rejected on evidence: the
vault had already adopted §5.3's tier names and §7's actor prefixes for their own sake, so the
vocabulary was buying interop while the ADR claimed it could not; what the bound actually
protected was two toolchain contracts, which the deviation register now names individually).
**A bare version number as the anchor** (rejected: v0.2 was amended in place the day after
adoption, and nothing noticed).

## Consequences

The decision and the mechanism are severable: if OKF stagnates or a stronger survivability
standard emerges, the mechanism is replaced by amending this ADR — the decision itself is not
reopened. While OKF is the mechanism, conformance tracks it as it evolves. That obligation is
discharged by the pin and the probe, not by intention: a hash mismatch is a finding, and
reconciling it is the work. Accepted knowingly for a young, currently one-vendor spec.

The reserved files (`index.md`, `log.md`) are constraints on the vault scaffold, and their
shapes are OKF's, not ours. Adopting an OKF family means the vault gains a second spelling of
data it already holds; that redundancy is the price of a consumer needing no research-vault
knowledge to read the bundle. Revisit the mechanism (not the decision) if a future OKF version's
structural rules start imposing real costs on the vault's own tools.
```

### 8.3 What the proposed text changes, and why

| Change                                                                                                                  | Closes                                |
| ----------------------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| §11 quoted verbatim, with §3.1's reserved-ness definition spelled out                                                   | D1, and the license for §1.3          |
| The "OKF instructs consumers to tolerate nonconforming files" clause deleted outright                                   | D2                                    |
| §8/§9's actual requirements stated where the old text stated OKF's MAYs as rules                                        | D3, and the license for §1.1 and §1.2 |
| "Structural and semantic", with the two toolchain contracts named individually instead of a blanket "no interop" claim  | D4                                    |
| Commit + hash pin, and reconciliation discharged by the probe rather than by intention                                  | D5, D6                                |
| "No OKF-reserved key carries a value OKF would misread" stated as a rule of the mechanism                               | §2.1, §2.2, §2.3                      |
| "Every family carries a disposition; silence is not a disposition", pointing at the register                            | §3, D10                               |
| The load-bearing surviving deviation named and scoped to rendering, with the rest delegated to the register             | Overcounting and undercounting alike  |
| A new rejected option recording why the old vocabulary bound was wrong                                                  | Keeps the reversal auditable          |
| The `inbox/` exemption stated with its scope-plus-workflow rationale instead of silently reversing or keeping the bound | §1.3's ruling                         |

The `Status` line keeps the original acceptance date: the decision is unchanged and only the
mechanism's statement is corrected, which is the severability this ADR has always claimed.

## 9. Closing the residual

### 9.1 It is two gaps, not one, and they have different owners

Per-claim attribution differs from §5.1 in two independent ways.

**The marker gap is ours.** OKF joins a claim to a source with an inline `[^id]` footnote whose
label is a `sources[].id`; the vault joins it with an inline `[@citekey]` whose label is the
citekey. Same shape, same join, different token. This one is closeable by us.

**The locator gap is OKF's.** `[@citekey, p. 12]` carries a pinpoint that parses losslessly to
CSL `locator` + `label`. OKF v0.2 has no locator or pinpoint concept anywhere: neither string
appears in `SPEC.md`, and its one use of "page" is `page reads` as a `usage_count` example
(`SPEC.md:325`), not a citation pinpoint. Worse, §5.1's own resolution model forecloses the obvious
workaround: putting the pinpoint in the footnote's prose (`[^smith2020]: Smith 2020, p. 12`)
leaves it exactly where §5.1 tells consumers not to look, since they "resolve attribution
through the matching entry, not by parsing the footnote prose". Moving it into the label
(`[^smith2020-p12]`) would mint a per-pinpoint source id, which is the second identity
[ADR 0004](../adr/0004-citekey-is-the-only-identity.md) exists to forbid. So a perfect §5.1
projection still loses the pinpoint. Nothing the vault does closes this.

One approach is ruled out empirically before the alternatives start. **Dual-emission in the
living vault does not work**: `[@smith2020, p. 12][^smith2020]` renders through
`pandoc --citeproc` as `[Smith (2020), p. 12][1]` with a matching footnote — reader-visible
duplicate attribution in every rendered manuscript. A definitions-only block without inline
markers fares no better: pandoc drops it and warns `Note with key 'smith2020' defined ... but not used`, and Obsidian shows an orphan.

### 9.2 The one argument worth making first

Before proposing to close the marker gap, it is worth being clear that the vault's form is not
a weaker rendering of §5.1's — under the vault's own rules it is a stronger one.

`skills/evidence-conventions/SKILL.md` states the constraint the claim grammar is built around:
claims get copied between notes, and "whatever is not on the line does not travel with it, so
attribution held in frontmatter survives exactly one hop". An OKF `sources[].id` is scoped to
one document's frontmatter, so a claim carrying `[^rev-policy]` into a second document arrives
pointing at nothing. A citekey resolves globally, in every document, forever.

§5.1's own rationale is the same principle one step short: labels are keyed rather than
positional "because agents constantly rewrite these documents: a positional index misattributes
silently the moment the list is reordered, whereas a stable `id` survives reordering". The
vault applied that reasoning to the next failure mode — agents *copy* as well as reorder — and
reached a globally stable key. That is adherence to §5.1's principle past the point §5.1 itself
takes it, which is the case any proposal below should make rather than apologize for.

### 9.3 Alternative A — adopt `sources` on literature notes (the floor)

Already Tier 4. Machine-write `sources: [{id: <citekey>, resource: <doi-url>, title: …}]` on
each literature note from data the importer already holds, leave prose untouched, and record
the rendering difference as one class-1 row in `docs/terminology.md` §3.

- **Closes:** nothing in the marker gap, and the report's earlier claim that it closed "the
  source half" was wrong. §5.1's join is document-scoped — a `[^id]` label resolves into *that
  document's* `sources` list — and the citations that need resolving live in `synthesis/` and
  `projects/` notes, which this never touches. What it does buy is real but different: each
  literature note becomes self-describing, declaring the external material it derives from in
  the field a cold consumer actually reads.
- **Leaves open:** the whole marker gap, and the locator.
- **Cost:** near zero on the import path. Not unconditionally free: §5.1 makes `resource`
  REQUIRED per entry, so a DOI-less source needs a resolvable URL or a §5.1 scope descriptor.
- **Verdict:** do it regardless. It is the precondition for A′ and B and the evidence for G.

### 9.3a Alternative A′ — extend `sources` to the citing notes

The thing that would actually close the source half. Derive a `sources` block on each
`synthesis/` and `projects/` note from the citekeys its claim lines already carry, so a
consumer reading the note where the citation lives can resolve it document-locally, exactly as
§5.1 intends.

- **Closes:** the source half of the marker gap, in the notes where it matters.
- **Leaves open:** the literal `[^…]` token, and the locator.
- **Cost:** more than it looks, though less than first priced. Project-note frontmatter
  already has machine writers — `_set_status` rewrites `status` and `record_pass` appends
  `verified` at publish (§1.5, §2.1) — so the precedent exists on that surface. Synthesis
  frontmatter has none, and the synthesis layer is authored prose (§2.3), so there this
  introduces a machine-maintained region into a human/LLM-owned surface — the tension the
  literature note's managed region answers, unanswered here. Needs a design pass, not a patch.
- **Verdict:** the honest middle option between A and B. Cheaper than B, and unlike B it
  improves the *living* vault rather than only the exported artifact.

### 9.4 Alternative B — project a conformant bundle at the publish boundary

`mark-published` already runs a closed gate, commits, and tags. Add a projection step that
renders the published project and the literature notes it cites into an OKF bundle: rewrite
`[@citekey, locator]` to `[^citekey]`, emit the matching `sources` entries, convert wikilinks
to relative markdown links, and drop Dataview fields into frontmatter or prose.

This needs a **new** check id and a new seam. The `render` id is taken: it is a live
import-side hold class for render rejections (`research_vault/__main__.py:278-296`,
`inbox.py:77`), wired 2026-08-22 and test-pinned at `tests/test_cli_live.py:1502,1538`.
Repurposing it would be exactly the class-4 collision §2.1 condemns. Under terminology.md §4.3's
"other projection or derivation" branch the new verb is an imperative verb-noun kebab —
`project-bundle` or similar — with a matching check id, ruled at §4.4.

**Pre-empting the obvious objection.** ADR 0001 already rejected an option by this name:
"**Export-boundary-only projection** — emit a conformant bundle only when publishing (rejected:
insures published output, not the living vault)." That rejection stands and this is not that
proposal. It was rejected *as the survivability mechanism*, in place of conformance in the
living vault. Here the living vault is already conformant by Tiers 0–4, and the projection adds
a second, stricter rendering on the artifact that leaves the vault. The rejected option was a
substitute; this is a superset.

- **Closes:** the marker gap completely, on the artifact a stranger actually receives.
- **Leaves open:** the locator, which no projection can carry (§9.1).
- **Cost:** real. A renderer, a fidelity check that the projection preserves every claim's
  attribution, and a decision about where the bundle lands (a `published/` tag payload, a
  sibling directory, a release artifact). This is the largest single item in the report.
- **Verdict:** the right answer once the projection seam (`project-bundle` or similar) is
  built. Not worth building the seam *for* this alone.

### 9.5 Alternative G — close the locator gap upstream, in OKF

The locator gap is a defect in a young spec, not a deviation by the vault, and OKF is actively
maintained — `SPEC.md`'s only commit since adoption is a substantive normative change merged
eleven days before this audit. Filing it is cheap, and it is the one path to a literal 100%.

Draft issue text, lead with the demonstrable defect rather than an adoption claim:

> **§5.1 has no way to attribute a claim to a *place* in a source.** A concept can say a claim
> came from `sources[].id = rev-policy`, but not that it came from page 12 of it. For
> scholarly and legal corpora the pinpoint is the attribution — "Smith 2020" and "Smith 2020,
> p. 12" are different claims about where the evidence sits, and a reader cannot check the
> second from the first. The workarounds §5.1 leaves open both fail: a pinpoint in the
> footnote prose lands where the spec tells consumers not to look ("consumers resolve
> attribution through the matching entry, not by parsing the footnote prose"), and a pinpoint
> in the label mints a new `sources` id per citation, which defeats the stable-key rationale
> the same paragraph gives. Suggested minimal addition, additive under §12: allow a footnote
> label of the form `<sources-id>@<locator>`, or admit an optional per-reference
> `{ id, locator, label }` form, with `label` drawn from the CSL locator vocabulary that
> existing scholarly tooling already emits.

- **Closes:** the locator gap — the only mechanism that can.
- **Cost:** filing is minutes; acceptance is outside our control and unbounded in latency.
- **Verdict:** file it and cite the issue in the deviation row. An open upstream issue is a
  materially different record from an unexplained deviation: it says the gap is in the standard
  and is being worked, which is what tracking a young spec is supposed to look like.

### 9.6 Alternative D — switch to note-style citation (considered, rejected)

CSL has note styles; with one, `pandoc --citeproc` puts every citation in a footnote by
itself, and the claim line's citation would render as the footnote OKF asks for, locator
included, with no dual-emission.

Rejected: it forces a citation style on the researcher's manuscripts to satisfy a metadata
format. This vault's field is health research — PRISMA, GRADE, Cochrane are its method
vocabulary (`docs/terminology.md` §2 T4) — and that literature is author-date nearly without
exception. Trading the output style of every manuscript for conformance in the vault inverts
[ADR 0001](../adr/0001-vault-outlives-its-tools.md)'s premise that the vault serves the
researcher and the tooling serves the vault. Worth naming so the option is visibly priced
rather than unconsidered.

### 9.7 Recommendation

They compose; this is not a choice among three.

| When                            | Do                                             | Why                                                                                                                                |
| ------------------------------- | ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Now                             | **A** — adopt `sources` on literature notes    | Already Tier 4. Makes literature notes self-describing and is the precondition for A′ and B. Does not itself close the marker gap. |
| Next, by design pass            | **A′** — extend `sources` to citing notes      | Closes the source half where the citations actually are. Needs a ruling on machine-owned frontmatter in a freely-rewritable layer. |
| Now, in parallel                | **G** — file the locator issue upstream        | Minutes of work, and it converts the residual from "we deviate" into "the standard has a gap, tracked".                            |
| When the projection seam exists | **B** — project a conformant bundle at publish | Closes the marker gap on the artifact that leaves the vault. Needs a new check id (`project-bundle` or similar), not `render`.     |
| Never                           | **D** — note-style citation                    | Priced and declined.                                                                                                               |

With A and G done, the recorded deviation reads honestly and completely: the vault joins claims
to sources by a globally stable key rather than a document-scoped one, which strengthens
§5.1's stated rationale rather than declining it; the rendering difference is a class-1
toolchain mismatch; and the pinpoint gap is upstream issue `<n>`, not a vault decision. The
marker gap stays fully open until A′ or B lands — A alone does not narrow it — and the pinpoint
gap stays open until OKF moves. Literal 100% needs B *and* G; everything short of that is an
honest, completely recorded deviation, which is a different and achievable claim.
