# Proposed ADR and CONTEXT.md changes

Status: **PROPOSAL — nothing in this document has landed.** ADR files are
written only after a decision is approved. The accepted register contains ADRs
0001–0004. Do not reserve ADR 0005 until a decision is approved.

## 1. Scope and review questions

This proposal addresses two documentation problems: an unaccepted draft was
placed in the ADR register, and the root and shipped vault glossaries have
drifted. It also classifies decisions that may need an ADR later.

It does not change the product contract, promise another host, or ratify an
architectural decision. Review asks whether to:

1. make `CONTEXT.md` the canonical glossary and generate the vault glossary
   from it; and
2. promote Better BibTeX ownership of the raw bibliography export to the next
   ADR.

The former open-standards draft remains background in this proposal, not an
accepted ADR.

## 2. Recommended documentation changes

### 2.1 One canonical glossary

[CONTEXT.md](../CONTEXT.md) is the meaning layer, but the shipped
[vault glossary](../knowledge_harness/templates/vault/system/glossary.md) is a
second, manually edited glossary. They already differ in both terms and
meaning: each has terms absent from the other, and they define the bibliography
export, screening state, and update notice differently.

**Recommendation:** `CONTEXT.md` owns each canonical definition. Render the
vault glossary from selected root entries plus a small vault-specific title and
introduction overlay. Do not keep two editable definition bodies. A parity test
can protect the migration, but it is not a substitute for one source of truth.

### 2.2 What belongs in CONTEXT.md

`CONTEXT.md` should remain a concise, project-specific dictionary: a term, its
meaning, and `_Avoid_` alternatives. That is not redundant with
[`docs/terminology.md`](terminology.md), which records naming authority and
provenance, or ADRs, which record choices and their consequences.

A definition should state what a thing is and include only properties needed to
distinguish it. Keep semantic distinctions such as Admission versus Import and
Citable versus Bibliography export. Trim rules, rationale, and literal
representation details when the glossary is revised:

| Current material | Proposed home |
| --- | --- |
| Vault's OKF mechanism and survivability rationale | ADR 0001 |
| Synthesis-layer writer and rewrite policy | ADR 0003 or vault instructions |
| Managed-region markers and direct-edit restriction | Generated vault instructions |
| Review-inbox orientation procedure | Workflow documentation |
| Verified-event and acknowledgment transition/retention rules | ADRs 0002 and 0003 |

The Citekey definition also needs correction: it is the vault's sole source
address, but its stability is an operating discipline over a user-editable
Better BibTeX key, not an intrinsic property ([ADR 0004](adr/0004-citekey-is-the-only-identity.md)).

### 2.3 Citability boundary

| Artifact | Meaning | Relationship |
| --- | --- | --- |
| Raw Better BibTeX export | Whole-library universe of items a citekey can name | It is broader than what is citable. |
| Citable set | Exported item with a literature note that is neither excluded nor superseded | It is the set claims may cite. |
| Future generated BibLaTeX bibliography | Harness-produced projection | It should match the citable set, not the raw export. |

Keep the distinction between the two current layers. If added, the future
projection should preserve it. A scoped external export would look simpler, but
would make citation resolution and project boundaries depend on external
collection curation.

### 2.4 Proposed CONTEXT.md inventory

All terms below should project to the vault glossary unless the routing note
says otherwise. These are proposed definitions, not accepted terminology.

| Group | Terms and proposed treatment |
| --- | --- |
| Bibliographic identity | **Bibliography export**, **Citable**, and **Citekey**: clarify the boundary in §2. Add **Citation locator** (a page, section, or other pinpoint; not source identity) and **Venue** (the journal, repository, or outlet where an item appeared). |
| Vault structure and ownership | Add **Synthesis note** (one page in the synthesis layer), **System folder** (support artifacts), and **Machine surface** (a path or durable field with a designated mechanical writer, broader than a Managed region). |
| Verification and review | Add **Verification surface** (`audit`, `commit`, or `publish`, selecting the closing checks), **Finding** (a review-inbox record for a non-MATCHED outcome), and **Reason code** (the governed leading classifier for a durable explanation). |
| Research and publication records | Add **Search run** (a completed retrieval query, including zero results), **Not-admitted candidate** (a considered source intentionally not admitted to Zotero), **Publication disposition** (publish, park, correct, or withdraw), **Project lifecycle state** (draft, parked, published, corrected, withdrawn), and **Update notice** (a registry signal with separate notice and detection dates). |

**Routing question:** decide whether to retain Analysis, Report, and Closing
check in the root glossary; project them only if a vault user encounters them
directly.

## 3. ADR triage

### 3.1 Advance for decision: Better BibTeX owns the raw export

**Decision shape:** Better BibTeX is the sole content writer of
`system/bibliography.json`. The harness observes the auto-export, compares it
with an on-demand Better CSL export, and commits only the exact matched
snapshot. It never synthesizes, hand-edits, or replaces the raw export.

This is the clearest candidate for the next accepted ADR. It selects an
authority and provenance boundary among real alternatives: a harness-generated
export, a manually maintained export, or a scoped external export. Reversing
it would affect citation resolution, snapshot provenance, user workflows, and
recovery from concurrent export changes.

If approved, the ADR should record that durable boundary and its consequences,
not the current polling, private-index, or compare-and-swap mechanics. The
ADR must also say that the raw export is not the citable bibliography.

### 3.2 Defer or keep below the ADR line

| Topic | Classification | Reason |
| --- | --- | --- |
| Evidence layer as a projection | Defer | Its authority boundary remains coupled to the evolving user-control model. |
| Deterministic-only closure | Defer | The foundation specification already parks it while the control model moves. |
| Zotero admission authority and one-way projection | Defer as a separate candidate | The trade-off is ADR-grade, but the operating rule is already documented and two-way synchronization remains deferred. |
| One designated writer per machine surface | Define the term; reconsider later | It is a real authority boundary, but must not be phrased as “CLI-only” or bundled with BBT export ownership. |
| Candidate-bound verification transaction | Implementation invariant | Immutable candidates, allowlisted outputs, and atomic application matter; the present mechanics remain replaceable. |
| Armed publish-gate bypass | Covered by ADRs 0002 and 0003 | It is a host enforcement protocol for fail-closed publication and durable records. |
| Archive at import | Workflow rule | `archive-source` remains separate from import, so same-session archival is not yet one enforced transaction. |
| Publication disposition history | Covered by ADR 0003 | Deprecate-never-delete already explains the append-only history. |

### 3.3 Separate scope and background, not knowledge-harness ADRs

| Topic | Current treatment |
| --- | --- |
| Applicable industry standards | A proposal-level principle: prefer the applicable standard when the product exposes an interoperability boundary. It does not create a boundary or select a protocol by itself. ADR 0001 already records the concrete OKF decision. |
| Host compatibility | A roadmap item, not a standards decision. Record support later in a matrix naming host, supported behavior, acceptance test, owner, and review trigger. Claude Code is current; Codex has no adapter, MCP surface, or cross-host acceptance suite. |
| Companion plugin layering | A separate design candidate. Its [rethink audit](research/rethink-audits/2026-08-25-coding-companion-plugin-layering-rethink-audit.md) defines an execution-discipline module, repo-policy module, doctrine, and bridge; it confirms layering as the target but conditions it on a maintained bridge. Do not decide it or add it to this ADR register here; revisit it in the Companion's own context. |

## 4. Follow-up sequence

1. Decide whether the one-source glossary rule is correct and select the
   proposed terms to add or revise.
2. If approved, implement the glossary projection and selected definitions in
   one change.
3. Decide whether the Better BibTeX authority boundary merits ADR 0005.
4. Keep all other items unnumbered until a specific decision passes the ADR
   test: hard to reverse, surprising without context, and chosen among real
   alternatives.

## Style reference

Use the Sandcastle ADR set as a style reference: state one specific decision,
its boundary, and its consequences.

- [A short Sandcastle ADR](https://github.com/mattpocock/sandcastle/blob/main/docs/adr/0001-per-step-timeouts.md)
- [A detailed Sandcastle ADR](https://github.com/mattpocock/sandcastle/blob/main/docs/adr/0007-worktree-locking.md)
