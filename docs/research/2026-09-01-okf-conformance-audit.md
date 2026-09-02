# OKF v0.2 conformance audit

Audited 2026-09-01 against the Open Knowledge Format v0.2 specification as published at
`GoogleCloudPlatform/open-knowledge-format@ad30107` (`SPEC.md`, 37748 bytes, last amended
2026-08-21). Method: eight per-section finder agents over the enumerated writer surfaces,
then one adversarial verifier per finding required to re-derive both the spec quote and the
`file:line` evidence independently. 83 findings raised, 65 survived, 18 refuted; the survivors
are deduplicated across dimensions into the items below.

Every item below carries a spec clause and a repo location. Nothing here is applied; this is
a review. `docs/terminology.md` and the ADRs carry uncommitted working-tree changes and were
not touched.

## Verdict

The vault is **not** a conformant OKF v0.2 bundle, and the gap is smaller than it looks. Three
findings fail §11's numbered bundle-conformance rules; two more fail its enumerated consumer
MUST — the tool reading a vault, not the vault's own files. All five are mechanical and none
costs the vault any semantics to fix. Everything else is either a reserved-key collision the repo's
own naming rules already forbid, an optional family left unadopted, or documentation that
misdescribes the spec.

The root cause is single and documentary: [ADR 0001](../adr/0001-vault-outlives-its-tools.md)
restates OKF's conformance rules from memory rather than quoting §11, and every structural
violation below traces to that paraphrase. The doctor `okf` probe then implements the
paraphrase, so it reports `OKF artifacts conformant` over a vault that is not.

| Bucket                    | Count | Meaning                                                      |
| ------------------------- | ----- | ------------------------------------------------------------ |
| Rule violation            | 5     | Fails OKF v0.2 §11 — three bundle rules, two consumer MUSTs. |
| Namespace collision       | 3     | An OKF-reserved key carries foreign values.                  |
| Unadopted optional family | 6     | Conformant, but the spirit gap.                              |
| Documentation defect      | 11    | The repo misdescribes the spec it conforms to.               |
| Confirmed conformant      | 9     | Worth keeping and worth recording.                           |

## 1. Rule violations

§1.1–§1.3 fail §11's numbered rules, which is what defeats ADR 0001's bundle-conformance claim.
§1.4–§1.5 fail the consumer MUSTs §11 enumerates by name — the tool misreading a conformant
vault rather than writing a nonconformant one.

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

**Two honest exits.** (a) Adopt: have `evidence-conventions` open a fleeting note with
`type: "fleeting"` and drop the exclusion — §4.1 explicitly does not register type values, so
this costs one line per note. (b) Record it: amend ADR 0001 to declare `inbox/` an exception,
give it a `docs/terminology.md` §1 cost class, and change the probe's success string to name
what it did not check. What is not available is the current position, which is neither.

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
deterministic pass on that note is dropped with no event, no error, and no finding. Because
ADR 0002's fail-closed publish gate rests on `verified` events (`publish.py:368`), the note
degrades into an unexplained publish block.

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
`templates/vault/system/templates/literature.md:6`, `CONTEXT.md:74`) and project publication
states (`draft`/`parked`/`published`/`corrected`/`withdrawn`, `publish.py:206`) into that same
key. `docs/terminology.md:69-70` frames both as declining "OKF document lifecycle" at cost
class 2. That is the wrong frame: nothing is *lost* by carrying both, so class 2 does not
bind; what is happening is class 4, and the table's own rule then requires the vault's field
to be renamed.

**Fix.** Rename to `screening-state` and `publication-status` (both already the CONTEXT.md
names), freeing `status` to carry a real §5.4 value — `stable` for an included note,
`deprecated` for a superseded one — projected additively. Both spellings coexist; §4.1
guarantees the extension keys survive.

### 2.2 `verified[].at` is a calendar date, not an ISO 8601 datetime

§5: "Every timestamp-valued key in OKF is an ISO 8601 datetime with an explicit UTC offset,
for example `2026-06-30T14:00:00Z`."

`events.py:26-32` requires `YYYY-MM-DD` and `events.py:102-104` writes it. Actual bytes:
`verified:\n  - {by: "research_vault/0.1.0", at: "2026-09-01", check: "doi"}`. Note the
contrast with `generated.at`, which `notes.py:213-220` renders correctly as Z-suffixed ISO —
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
`generated: {by: "{{ACTOR}}", at: "{{NOW}}"}`. A repo-wide grep finds `{{ACTOR}}`/`{{NOW}}`
only in those three files — no Python and no skill step substitutes them, and
`scaffold.py:216` copies them verbatim into every scaffolded vault.

`skills/project-flow/SKILL.md:48` makes this concrete: project notes are authored prose, "no
CLI verb is involved", so the agent either carries the literal placeholder into durable
frontmatter or invents an actor — the exact case §7 makes a producer MUST. A §5.2 consumer
reading `generated.at` gets an unparseable literal.

**Fix.** Either delete the line (§5: "All are optional. Their absence carries meaning" — but
this contradicts `foundation-spec.md:61-62`, which requires generation metadata, so the spec
needs the matching amendment), or have the skills write
`generated: {by: "human:<id>", at: "<generated_at_now()>"}`, reusing `notes.py:213`.

## 3. Unadopted optional families

All conformant. Each needs a disposition — adoption or a recorded declination — because
`docs/terminology.md` §3 requires one and silence currently stands in for both.

| Family                        | Status                           | Recommendation                                                                                                                                                                                                                                                                                                                                                                                               |
| ----------------------------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `resource` (§4.1)             | Never written                    | **Adopt.** Free. Literature notes already carry `doi`/`url` (`notes.py:229-236`); `resource: https://doi.org/…` names the paper, not the note.                                                                                                                                                                                                                                                               |
| `sources` (§5.1)              | Never written                    | **Adopt.** `sources: [{id: <citekey>, resource: <doi-url>, title: …}]` from data in hand. `resource` is REQUIRED within an entry, so the DOI must carry — the citekey alone is not enough.                                                                                                                                                                                                                   |
| `title`, `description` (§4.1) | Never written                    | **Adopt.** Both values are already in hand at render time; `description` feeds §8 index entries and search snippets.                                                                                                                                                                                                                                                                                         |
| `tags` (§4.1)                 | Never written                    | Assess. Obsidian tags exist; whether they belong in OKF `tags` is a modelling call.                                                                                                                                                                                                                                                                                                                          |
| `stale_after` (§5.5)          | Declared pass-through, no writer | Decide: wire it to the `staleness` probe, or drop the pass-through claim.                                                                                                                                                                                                                                                                                                                                    |
| Attested Computation (§10)    | Wholly unadopted                 | **Record the declination.** Not required by §11, and `fixity-sha256` / the bibliography byte-comparison genuinely cannot be attested consumer-side. But two candidates are real: `managed-sha256` and the quote check are sanctioned computations whose definitions live only in the tool, not the bundle. Also note `trust_tier` folds per-run state into the doc-level tier §10.6 defines as verification. |

### 3.1 The `sources`/`resource` declination rests on a claim the spec does not make

`docs/terminology.md:67` declines `sources`/`resource` because "the citekey is source
identity" ([ADR 0004](../adr/0004-citekey-is-the-only-identity.md)). ADR 0004's argument is
about minting a second *identity*; neither field is one. §2 makes the Concept ID the file
path — which in this vault already *is* the citekey (`notes.py:129`) — and §5.1's `id` is
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

**Fix (free).** `- [literatures/](literatures/) — …` and
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
projection and no pandoc render step (the `render` check id is registered but unimplemented).
Building that seam is the only path to adopting §5.1 without touching the toolchain, and it is
a larger piece of work than anything else in this report.

## 4. Documentation defects

Nine of the eleven are in one paragraph. `docs/adr/0001-vault-outlives-its-tools.md:7`
restates §11 from memory, and each misstatement licensed a violation above.

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
  ISO 8601 datetime (`notes.py:213-220`).
- **§7 actor convention** followed exactly by every code-written record —
  `research_vault/<version>` and `human:<id>`.
- **§5.3 trust tiers** — `unverified` / `machine-confirmed` / `human-reviewed`, the spec's
  three names verbatim, derived rather than stored.
- **§12 `okf_version`** declared with the exact key, value form, and location.
- **Nested `index.md`** correctly frontmatter-free, and test-pinned.
- **Rule 2** holds on every non-reserved concept document, mechanically enforced.
- **The citekey filename is the OKF Concept ID** (§2). The vault implements OKF identity
  rather than declining it.
- **No §10 key or the `Attested Computation` type name is squatted.**
- **Broken links never fail the probe**, matching §6.1's tolerance requirement.
- Synthesis notes use §5.4's value set verbatim (`draft`).

## 6. Checked and cleared

Three finder agents reported ADR 0001's spec pointer
(`github.com/GoogleCloudPlatform/knowledge-catalog`, `okf/SPEC.md`) as stale. **It is not.**
Verified 2026-09-01: the URL returns HTTP 200, and the file is byte-identical to
`open-knowledge-format/SPEC.md` (both 37748 bytes, `diff` clean). The spec now also has its
own dedicated repository, and the ADR's pointer names a mirror inside a product repo — worth
updating for clarity, but it resolves. The only real gap is the missing commit pin (D5).

Also cleared: non-adoption of §10 is not a §11 violation; claim-link wikilinks are conformant;
`references/` (§6.3) is explicitly "a naming convention, not a requirement".

## 7. Path to 100%

Ordered by the repo's own maxim — eliminate the problem, then add a mechanism, then a rule,
then prose. Tiers 0–2 close every §11 violation.

**Tier 0 — producer fixes, no semantics lost.**

1. Delete `type: "index"` from the root index template (§1.1).
2. Emit date-grouped, newest-first `log.md` (§1.2).
3. Convert the two machine-written navigation surfaces to relative markdown links (§3.2).
4. Substitute or delete the `{{ACTOR}}`/`{{NOW}}` placeholders (§2.3).
5. Give fleeting `inbox/` notes a `type`, or declare the exception (§1.3).

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

**Tier 2 — reader tolerance in `events.py`** (§1.4, §1.5). Write path unchanged; ADR 0002
untouched.

**Tier 3 — vacate the reserved key.** Rename to `screening-state` / `publication-status`,
optionally dual-emitting a real §5.4 `status` (§2.1).

**Tier 4 — additive adoption**: `resource`, `sources`, `title`, `description` (§3).

**Tier 5 — record what remains.** Correct ADR 0001's four misstatements (D1–D4); pin its spec
reference (D5); retract or qualify the conformance claims in `foundation-spec.md:16` and
`CONTEXT.md:9` until Tier 0–2 lands (D7); delete the phantom `identity merge` row and split the
`sources`/`resource` row (D8, D9); restore the OKF adoption block §3 mandates (D10); add the
missing deviation rows — claim-link syntax, the `check` extension and coverage-based tier
derivation, `verified[].at` precision, and the §10 declination; add the frontmatter sentence
to `synthesis-conventions` (D11).

The deviations that survive all of this and remain correct are three: pandoc citations over
§5.1 footnotes (class 1, and no export seam exists to escape it — §3.3), stance-typed claim
links over §6.1's untyped relationships (class 2), and Obsidian block-link claim addressing
(class 1, currently unrecorded). Everything else on the current deviation table either does
not need to be a deviation or does not correspond to anything in the spec.
