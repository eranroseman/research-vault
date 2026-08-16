# Rethink audit — foundation spec

Clean-slate redesign audit of [docs/specs/2026-08-16-foundation-spec.md](specs/2026-08-16-foundation-spec.md), run before approval at the author's request, with the widest prior-art net: products, mass-deployed systems, standards, and peer-reviewed literature. Method: rethink-audit (requires → prior-art → design → gap → migrate → trade-offs). Raw findings: [research/raw/wide-prior-art/](../research/raw/wide-prior-art/) — 85 findings, each verdict-tagged CHANGES-SPEC / CONFIRMS-SPEC / IRRELEVANT.

## requires:

R1 zero fabricated citations, claims traceable to source + locator, defensible under review (`adr` #13) · R2 foundation + slice now, other arcs later (`adr`) · R3 solo researcher, WSL2 + Zotero 9 + BBT, **Zotero-only** (`caller`) · R4 user-driven control, predictability over autonomy (`adr` #11) · R5 plain-markdown git vault, ecosystem conventions (`adr` #7/#8) · R6 Zotero = sole evidence admission, human act (`adr`) · R7 mechanical verification; LLM never blocks; outage ≠ fabrication (`adr` #10) · R8 provenance supports later rot-watch without retrofit (`adr`) · R9 globally enabled beside dev harness (`adr` #12) · R10 shareable self-sufficient plugin (`adr` #11) · R11 both flows owned; project flow is the entry (`caller`) · R12 falsifiable validation (`adr` #14) · R13 deprecate-never-delete, contradictions preserved (`adr` #9) · R14 bounded attention: surgical holds, one drain (`adr`) · R15 Codex portability, later stage (`caller`) · R16 **no** institutional/compliance requirements (`caller` — regulated-science patterns count only where they serve R1).

## prior-art: (seven domains)

| Thread | Exemplars read | CHANGES / CONFIRMS |
|---|---|---|
| Systematic-review products | Covidence, Rayyan, EPPI-Reviewer, DistillerSR, MECIR, PRISMA-S, GRADE | 5 / 4 |
| Wikipedia citation machinery | WP:V, Citoid, Citation bot, IABot (300M links), RetractionBot, Perennial Sources | 6 / 7 |
| Fact-checking standards | ClaimReview, IFCN, ClaimBuster, C2PA ingredient chains | 6 / 5 |
| Research-object standards | RO-Crate, OAIS/NDSA, Force11, JATS4R, DOI RA routing | 6 / 6 |
| Agent-memory systems | Zep/Graphiti (bi-temporal), MemGPT/Letta, mem0 | 5 / 6 |
| Regulated-science evidence | 21 CFR Part 11, ALCOA+, MHRA GXP, ELN lock-on-sign | 5 / 8 |
| Sensemaking literature | Pirolli–Card, Heuer ACH, Shipman–Marshall, Whittaker, Hypothes.is anchoring | 5 / 7 |

**Confirmed core** (unanimous across domains): evidence/interpretation separation; admission control at ingestion; deterministic gates, human closure authority; LLM-as-second-reviewer-never-blocker (Rayyan deploys precisely this); deprecate-never-delete; contradiction preservation; append-only logs; proactive archiving. **The architecture stands — no structural redesign.**

## gap: (clustered deltas; all extend decisions, none reverse them)

- **A. Update-notice net too narrow** — 12 Crossref update types exist; blocking class must be {retraction, partial_retraction, removal, withdrawal}, warn class {expression_of_concern, correction, corrigendum, erratum}, reinstatement clears; RW matching on **PMID + DOI**; **non-Crossref DOIs (arXiv/DataCite) currently read as clean** — route by DOI registration agency; identifier discovery before SKIPPED (a DOI-less retracted paper must not be permanently exempt).
- **B. Trust-tier honesty** — verified events record their comparison target (managed-region vs source-text); events written only by deterministic surfaces with CI recomputation (the agent being audited must not mint machine-confirmed); three git-mechanical lints: append-only trails, published-drift, claim-immutability.
- **C. Anchor durability is day-one** — block IDs derive from stable content (managed-region re-render must never orphan claim addresses); capture quote prefix/suffix selectors at extraction, defer only the re-anchoring cascade.
- **D. Search provenance** — append-only search log (query-as-run, source, date, counts) + reason-coded not-admitted records; PRISMA's definition of a defensible trail.
- **E. Post-publish lifecycle** — corrected/withdrawn effort states; standing alerts against published efforts trigger a correction flow, not just next-publish blocking.
- **F–K.** Controlled reason-code vocabulary; confidence-reason required below high; inbox count+age surfacing (Whittaker rot); acks composed by skills, human supplies consent+reason (Shipman); per-quote human attestation when source text unextractable (Marshall sparsity); rejected/superseded-source lint (Perennial pattern); superseded-by links; contested-claim surfacing (ACH); bi-temporal retraction records (notice date ≠ detection date — load-bearing for the validation question itself); per-attachment fixity (OAIS); version designators (Force11); archive-at-import; Zotero-backup boundary stated; factored-verification selection policy (ClaimBuster); RO-Crate publish manifest → deferred.

## migrate:

One spec amendment pass before approval, ordered §5 schema → §6 gates/lints → §7 skills → §9 drill → §10 register. Applied 2026-08-16 (see spec git history for the diff).

## trade-offs:

Schema weight — machine-written at capture, friction ≈ 0 (flips only under hand-authoring, precluded by R4). Wider alert net → more inbox entries — tiered + age-surfaced (flips if slice shows warn-tier noise drowning solo attention → narrow warn class). Search log — one artifact per session, append-only (flips only under high-frequency casual search, not the design's intent).

**Verdict:** architecture confirmed by convergent independent domains; three genuine trust-boundary defects found and fixed (registry hole, block-ID fragility, verified-event forgeability); the rest are edge-hardening. Not "already sound" — but sound after one amendment pass.
