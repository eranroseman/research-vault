# Rethink audit — glossary duplication and ADR triage

Disposition: historical (2026-09-06)

Clean-slate design audit of the documentation subsystem behind
[docs/2026-08-28-proposed-adr-and-context-changes.md](../../2026-08-28-proposed-adr-and-context-changes.md):
the relationship between the root glossary, the shipped vault glossary, and
the ADR register's triage/acceptance workflow. Method: rethink-audit
(requires → prior-art → design → gap → migrate → trade-offs). Prior-art
sourcing:
[docs/research/prior-art/2026-08-28-glossary-generation-and-adr-triage.md](../prior-art/2026-08-28-glossary-generation-and-adr-triage.md)
(background research against primary sources).

## requires:

Two independent subsystems in scope: the glossary/terminology surface and the
ADR register.

**Glossary**

- R1 (`docs`) [CONTEXT.md](../../../CONTEXT.md) already claims meaning-layer
  authority ("this glossary is the meaning layer") — one canonical body, no
  second hand-edited body elsewhere.
- R2 (`caller`: vault end-user; `adr` 0001)
  [the vault glossary](https://github.com/eranroseman/knowledge-harness/blob/da637c9a0289ccf272bcf3a82db84bb2b54208ff/research_vault/templates/vault/system/glossary.md)
  ships standalone into every scaffolded vault; per ADR 0001 a vault carries no
  runtime dependency on research-vault, so any projection mechanism has to run at
  build/dev time, never at vault-runtime.
- R3 (`docs`, proposal §2.2) a definition states what a thing is plus only the
  properties needed to distinguish it; mechanism, rationale, and rule detail
  belong in the owning ADR or workflow doc, not the glossary.
- R4 (`tests`)
  [tests/test_templates.py:170](../../../tests/test_templates.py#L170) already
  hand-asserts byte-identity of the shared term subset — proof that
  single-wording-per-term is already treated as a requirement today, just
  enforced by the wrong mechanism.
- R5 (`adr` 0004; `docs` proposal §2.3) the bibliographic-identity boundary
  (raw export / citable set / future generated bibliography) stays
  distinguishable on every surface that uses these terms.
- R6 (`assumed` — the actual pain driving the proposal) editing a canonical
  definition once should propagate everywhere it is projected; no mechanism
  enforces this today.
- R7 (`adr` 0001) the projection mechanism cannot be a live runtime pointer
  from the shipped template back to this repo — the template file must stand
  alone once copied into a vault.

**ADR register**

- R8 (`assumed` + `caller`:
  [docs/agents/domain.md](../../agents/domain.md), which has every skill treat
  a file under `docs/adr/` as a binding accepted decision) a file enters
  `docs/adr/000N-*.md` only after review; an unreviewed draft must not carry
  `Status: accepted` or occupy a register slot.
- R9 (`docs`, proposal §4) a topic advances to ADR status only if it is hard
  to reverse, surprising without context, and chosen among real alternatives.
- R10 (`docs`, proposal's opening line) the register's numbering stays
  contiguous — no reserved-but-unspent numbers.

Caller sweep: every accounted caller is in-repo — the domain-modeling skill,
`scaffold.py`/its tests, `docs/terminology.md`, and the shipped vault
template. The sweep cannot reach any vault already scaffolded outside this
repo (ADR 0001 says vaults outlive their tools, so this audit has no way to
inspect or migrate those), nor any agent session that reads CONTEXT.md's
conventions from memory instead of a fresh read — that failure mode is
unenforceable from here.

## prior-art:

Full citations in
[docs/research/prior-art/2026-08-28-glossary-generation-and-adr-triage.md](../prior-art/2026-08-28-glossary-generation-and-adr-triage.md).

**Glossary generation**, verified against primary sources:

- OASIS DITA's `@conref`/`@conkeyref` — build-time transclusion, with context
  validity checked at resolve time. Supplies the underlying "one file includes
  a rendered block from another at build time" idea; the versioning/multi-repo
  apparatus around it in DITA doesn't transfer here.
- Microsoft API Extractor — generates a `.api.md` report, commits it to git,
  and fails CI hard on any divergence with no autofix path. This is the
  sharpest available match to "generate the template from CONTEXT.md, and
  test that the generated output matches what's committed."
- oclif's `readme` command — regenerates only a marker-delimited region of a
  file, leaving hand-written prose around it untouched. Matches the shape this
  proposal wants (regenerate one region, keep vault-specific framing around
  it) but ships no built-in staleness guard — the parity check has to be
  added separately, same as planned here.
- Jest's own snapshot-testing docs name the relevant failure mode directly:
  golden/snapshot tests degrade into rubber-stamping if regeneration isn't
  reviewed on every change — exactly the risk already realized by the current
  hand-typed byte-literal in `tests/test_templates.py`, which is worse than an
  ordinary checked-in fixture would be.
- This repo's own precedent, one layer down:
  [2026-08-24-vale-evaluation.md](../prior-art/2026-08-24-vale-evaluation.md)
  declined a generated `reject.txt` for the identical terminology-guard
  problem, choosing instead "a pytest that parses CONTEXT.md at test time — no
  generated artifact, so registry drift is structurally impossible," per
  AGENTS.md's own rung order (eliminate the problem > add a mechanism > add a
  rule). Full elimination isn't available one layer up, at the glossary body
  itself, because the shipped template must exist as a standalone file per ADR
  0001 — a deliberate, justified deviation from the repo's own precedent
  rather than an oversight.
- TBX/ISO 30042 and SDL MultiTerm/Trados solve terminology interchange for
  localization pipelines — a different weight class of problem, not adoptable
  prior art here.

**ADR triage**, verified against raw source text:

- Michael Nygard's 2011 post states only an "architecturally significant"
  scope filter — not a reversibility, contentiousness, or cross-cutting-impact
  test. It defines four status states (proposed, accepted, deprecated,
  superseded) and never addresses a record that skipped `proposed` and was
  wrongly `accepted`.
- adr.github.io adds nothing beyond Nygard's scope filter; it functions as a
  portal to templates and papers, not an independent source of criteria.
- MADR adds `rejected` as a fifth status, plus `decision-makers`/`consulted`/
  `informed` fields that have no solo-maintainer analogue.
- joelparkerhenderson/architecture-decision-record is the closest real match:
  it names "single-developer" explicitly as a reason to *skip* writing an ADR,
  and states immutability as an actual rule — amend or supersede an ADR,
  never erase it.
- None of the three primary sources discuss recovering from an unreviewed
  record that already occupies a slot in a numbered sequence. The proposal's
  fix — don't reserve a number until a decision is approved — is original
  synthesis, stronger than Nygard's own scheme (which presumes every numbered
  record validly passed through `proposed`), not an application of a settled
  convention.
- The proposal's three-part ADR test (hard to reverse / surprising without
  context / chosen among real alternatives): only "surprising without
  context" traces back to Nygard's stated rationale for keeping ADRs at all;
  "hard to reverse" and "chosen among real alternatives" appear in none of the
  three primary sources examined. The repo invented this test; nothing in the
  prior art contradicts it, so it stands, credited correctly as this repo's
  own synthesis rather than borrowed doctrine.

## design:

**Glossary** — one canonical body plus a dev-time generator plus an enforced
parity test, in the shape API Extractor uses:

1. [CONTEXT.md](../../../CONTEXT.md) stays the sole hand-edited definition
   body (R1), trimmed per the proposal's §2.2 routing table as part of the
   same change (R3).
2. A selection manifest — which terms project, plus the vault-specific title
   and intro overlay, resolving the proposal's §2.4 routing question — drives
   a generation script that renders
   [the vault glossary](https://github.com/eranroseman/knowledge-harness/blob/da637c9a0289ccf272bcf3a82db84bb2b54208ff/research_vault/templates/vault/system/glossary.md)
   from CONTEXT.md. This runs at repo dev-time only; the scaffold's existing
   static copy at vault-creation time is untouched (R2, R7).
3. Replace `tests/test_templates.py`'s hand-typed literal with a
   generate-then-diff test: regenerate the template in memory from CONTEXT.md,
   assert equality against the committed file, fail hard on any mismatch, no
   autofix path (R4, R6). This collapses three hand-sync points to one.

**ADR register** — make proposed-then-accepted an actually used workflow, not
just a documented one:

1. New ADR candidates are authored with `Status: proposed`; the flip to
   `accepted` happens only in a separate, later commit or session (R8) — this
   mirrors Nygard's own scheme, which per the research needs no modification
   for solo work, only actually being used.
2. A numbered slot is spent only at acceptance time (R10) — the proposal's own
   rule, already tighter than anything in the sourced material; keep as-is.
3. The register-entry test stays the proposal's three-part test (R9); no
   primary source offers an improvement on it.
4. For a record that was wrongly accepted and caught within the same session
   before anyone else read it (ADR 0005): plain removal is defensible, but the
   audit should state that reasoning explicitly rather than defaulting to
   deletion by habit. The general rule going forward, for anything that *has*
   already been shared or read, is mark-rejected-and-keep, per
   joelparkerhenderson's and MADR's immutability convention.

## gap:

| Requirement                                        | Current state                                                                                                                                                                                                                                                                                                                 | Divergence                                                                                                                                                                                          |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| R1 — one canonical body                            | [CONTEXT.md](../../../CONTEXT.md), [the vault glossary](https://github.com/eranroseman/knowledge-harness/blob/da637c9a0289ccf272bcf3a82db84bb2b54208ff/research_vault/templates/vault/system/glossary.md), and [tests/test_templates.py:170](../../../tests/test_templates.py#L170) each hand-carry the shared subset's prose | Three-way duplication, not the two the proposal document counts — the test's inline literal is a third body copy the proposal never named                                                           |
| R2/R7 — build-time-only projection                 | No generator exists; the template is a hand-typed static file that `scaffold.py` copies verbatim                                                                                                                                                                                                                              | No generator, no selection manifest                                                                                                                                                                 |
| R3 — trim mechanism/rule detail out of definitions | CONTEXT.md's Bibliography export / Screening state / Update notice carry different amounts of mechanism detail than the template's versions of the same terms                                                                                                                                                                 | Live drift today, confirmed by direct file read and independently by the research agent                                                                                                             |
| R4/R6 — no divergent wording between surfaces      | Synthesis note, System folder, and Venue exist as full entries in the vault glossary but are absent from CONTEXT.md entirely                                                                                                                                                                                                  | Live drift, already happened, uncaught until this audit                                                                                                                                             |
| R8 — accept only after review                      | ADR 0005 was committed with `Status: accepted` directly (commit `573489b`), with no `proposed` stage                                                                                                                                                                                                                          | Caught within the same session, but disposal sits uncommitted (`git status` shows `D docs/adr/0005-apply-open-standards-at-applicable-boundaries.md`) — unresolved limbo, not yet a closed gap      |
| R9 — the three-part ADR test                       | Lives only as prose in the new proposal document                                                                                                                                                                                                                                                                              | No mechanical enforcement anywhere (no hook, no template checklist); consistent with the repo's general pattern of testing only what's cheap to test mechanically, not flagged as urgent on its own |
| R10 — no reserved unspent numbers                  | ADRs 0001–0004 are accepted and well-formed, matching Nygard's Status/Considered Options/Consequences shape closely                                                                                                                                                                                                           | No gap on 0001–0004; only 0005 violates this                                                                                                                                                        |

## migrate:

1. Resolve the ADR-0005 limbo: commit the working-tree deletion with a message
   stating why (self-accepted without review, never externally relied on
   within or beyond this session) — closes the open gap.
2. Record the authoring rule (in the proposal document or a short process
   note — not a numbered ADR): new ADRs start `Status: proposed`; the flip to
   `accepted` happens only in a separate, later commit.
3. Trim CONTEXT.md per the proposal's §2.2 routing table: OKF mechanism and
   survivability rationale to ADR 0001, synthesis-writer/rewrite policy to
   ADR 0003 or vault instructions, managed-region rule to generated vault
   instructions, review-inbox procedure to workflow documentation,
   verified-event/acknowledgment rules to ADRs 0002/0003.
4. Decide the proposal's §2.4 routing question (keep Analysis, Report, and
   Closing check root-only, or project them too) and finalize the per-term
   projection manifest, including the vault-specific title and intro overlay.
5. Write the generation script that renders the vault glossary from
   CONTEXT.md plus the manifest from step 4.
6. Run the generator once, diff its output against the currently committed
   template, and reconcile the three already-drifted terms (Synthesis note,
   System folder, Venue) — decide per term whether it belongs at root too or
   is vault-only, then commit the now-generated file.
7. Replace `tests/test_templates.py`'s hand-typed literal with the
   generate-and-diff test (hard fail, no autofix).
8. Advance the Better BibTeX ownership candidate (proposal §3.1) through the
   now-actually-used proposed→accepted pipeline established in step 2 — the
   first real exercise of the fixed workflow, earning ADR 0005 properly this
   time.

## trade-offs:

- A generator plus manifest is one more moving part than hand-editing two
  files directly. This flips back toward plain hand-editing if term count and
  change frequency stay this low — but drift has already happened at this
  size (three terms, silently, before anyone noticed), so the added machinery
  is already earning its cost rather than guarding against a hypothetical.
- Deleting ADR 0005 outright (rather than marking it rejected and keeping it)
  forfeits its historical trail. This flips to mark-and-keep the moment any
  other human or agent session is confirmed to have read or acted on it
  before this fix — there is currently no evidence of that.
- Rule-tier enforcement of proposed-before-accepted (a documented convention,
  not a hook) is cheaper to set up now but relies on discipline holding. This
  flips to needing a pre-commit hook the moment concurrent ADR authorship
  becomes real — and AGENTS.md already states that parallel sessions share
  this checkout, which argues for building the hook sooner rather than after
  a second incident.
- Keeping the vault glossary as a generated-but-committed artifact, rather
  than a live include back into this repo, trades a small build step for
  correctness under ADR 0001's standalone-vault requirement. This flips only
  if ADR 0001 itself is reopened, which nothing in this audit suggests doing.
