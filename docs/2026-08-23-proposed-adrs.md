# Proposed ADRs and CONTEXT.md changes

Status: **PROPOSAL — nothing here has landed.** ADR files are written only after approval of the final version (author ruling, this session). Format follows the `domain-modeling` skill's ADR template; the three-part test (hard to reverse / surprising without context / real trade-off) gates every candidate below.

Method: seven grilling rounds with the author, plus a 26-agent sweep over the spec, the 2026-08-22 rulings, the no-fabrication audit, and the implementation — every candidate adversarially refuted by a fresh agent instructed to kill it. 13 of 24 survived; three edits the author had already approved were **reversed** by refutation and appear in §11 rather than as proposals.

## What is proposed

| Change                                                                   | Files                                               |
| ------------------------------------------------------------------------ | --------------------------------------------------- |
| Five new ADRs, 0004–0008 (0005 carries an A/B choice)                    | `docs/adr/`                                         |
| One scope-bound sentence added to ADR 0001                               | `docs/adr/0001-vault-outlives-harness.md`           |
| Five CONTEXT.md edits (two rewrites, one word-fix, two new terms)        | `CONTEXT.md`, vault glossary template               |
| Two terminology.md rows (the `digest` naming walk; the rename it forces) | `docs/terminology.md`                               |
| One post-Q batch item (`skipped_digest` → `skipped_sha256`)              | `docs/superpowers/plans/2026-08-22-post-q-batch.md` |
| One AGENTS.md clause — **pending the author's reading**, see §12         | `AGENTS.md`                                         |
| One spec edit — **already applied**, see §10                             | foundation spec §4, §10                             |

______________________________________________________________________

## 1. ADR 0004 — Human gates only where judgment can differ

# Human gates only where judgment can differ

Status: proposed (2026-08-23)

A human gate exists only where judgment can differ from one instance to the next. Repeated identical confirmations are a rubber-stamp factory: they train click-through, and a human who has learned to click through one gate carries that habit into every other gate in the system, including the ones that matter. The decision therefore bounds where gates may be placed, not just how they behave.

**Corollary for admission.** Where a decision has already been made over a curated list, the human act is the *decision*, not the typing: the list is reviewed once, the approval and the list hash are recorded as provenance, and the machine performs the entries through the reference manager's own consented write path. Per-item ceremony over an already-decided list is the failure mode, not the shortcut. Per-item gates stay exactly where per-item judgment is real — an ongoing research find, a classification a human must actually look at.

## Considered Options

Per-item confirmation everywhere (rejected: it looks like more control and delivers less — the slice's 170-URL admission is what exposed this, and the author's own review of that batch caught 17 genuine misclassifications precisely because it was a real judgment pass rather than 170 identical prompts). Silent bulk admission with no recorded approval (rejected: the decision then has no provenance, and admission is the vault's trust boundary).

## Consequences

Warn-tier precision becomes an obligation rather than a nicety: a warn-tier check class whose observed review-inbox precision collapses is itself a defect — to tune or to demote — because a noisy queue manufactures rubber stamps by a second route. The deterministic closing checks are exempt by construction. The review inbox needs a drain surface that reports count and age, since a warn queue nobody drains is the same failure wearing different clothes.

______________________________________________________________________

## 2. ADR 0005 — Absence is not a pass

**Option A (recommended): its own ADR, referencing 0002.** Draft:

# Absence is not a pass

Status: proposed (2026-08-23)

When a check has nothing to check, the result is not trust; when a value is unknown, no value is written. ADR 0002 fixed what a *result* may claim; this fixes what *emptiness* may produce, which is the gap four separate defects walked through.

**Vacuous satisfaction mints nothing.** An item with zero applicable checks derives `unverified`, never a machine tier: a subset test over an empty applicable set is vacuously true, and vacuous truth is not evidence. Trust-tier derivation carries an explicit floor — at least one MATCHED result — rather than inheriting one from set logic.

**No invented values on durable surfaces.** No padding of missing date precision, no placeholder strings written into fields other records key on, no substituting one field for another when the real one is absent, no arbitrary pick among ambiguous matches. Where a value is unknown the record says so — an honest four-state result, or an absent field plus a reason code in the review inbox — and never a value that reads as fact downstream.

## Considered Options

Vacuous truth as the natural implementation (rejected: a frontmatter-less file with no identifiers and zero verified events derives the top machine tier — the audit reproduced this by running it). Placeholders to keep pipelines flowing (rejected: the literal string `"unresolved"` reached a fixity field and then became the acknowledgment's scope anchor, so acknowledgments scoped to a constant instead of to content). Padding partial dates to a full one (rejected: invented precision then drove notice-ordering and persisted into inbox records and ack fingerprints).

## Consequences

Some items never reach a machine tier, and that is the honest outcome rather than a coverage bug to fix. Every writer of durable frontmatter needs an explicit absent-value branch. Spec rows that never define their absent-field outcome are under-specification defects, not implementer latitude. This extends ADR 0002 and does not amend it.

**Option B: collapse into ADR 0002** as two sentences — a floor sentence on tier derivation and a no-invented-values sentence on durable writes. Cheaper, no new file; the cost is that four audit defects lose the argued home that explains why each rule exists, and 0002's own subject (what a *result* certifies) stretches to cover what a *writer* may emit.

______________________________________________________________________

## 3. ADR 0006 — Two universes: what a citekey names, what this vault may cite

# Two universes: what a citekey names, what this vault may cite

Status: proposed (2026-08-23)

The bibliography export is the **source universe** — the whole-library Better BibTeX export that resolves a citekey to an item and supplies metadata for imports. `literatures/` membership is the **citation universe** — a claim's citekey is citable only if its literature note exists in this vault. The reference library is multi-project by nature, so library-present is not citable-in-this-vault, and a check that joins only against the export cannot tell an accidental cross-project citation from a legitimate one.

The remedy stays one skill invocation away: cite → registry-first import → the note exists → the check passes. No second membership file is introduced, because a separate allowlist would drift from the folder it claims to describe.

## Considered Options

Single universe (rejected: a never-imported citekey from another project reports MATCHED and publishes). A curated citable-items file (rejected: two records of the same membership, and the file loses). Scoping the export to a per-project collection (rejected as a trust boundary: it is a performance option, and it would put curation between admission and the citekey universe).

## Consequences

The citekey check's contract is tier-2, and it is currently unenforced in the implementation — tracked as a defect, not restated here. `literatures/` becomes the thing to keep honest: an import is what confers citability, so the evidence layer's never-free-written rule is what the whole gate rests on.

______________________________________________________________________

## 4. ADR 0007 — A digest is written from full text or not at all

# A digest is written from full text or not at all

Status: proposed (2026-08-23)

The digest — the authored account of what a source says, living in its literature note's free prose — is written from the source's full text, always and only. A digest expanded from an abstract is **fabricated facts**, not merely fabrication-shaped: expanding an abstract necessarily invents specifics it does not carry (methods, conditions, magnitudes) and attributes them to the source under its citekey, which is the same zero-tolerance class as a fabricated citation. Second reason, independent of invention: the abstract is the author's persuasion surface — what they want a reader to believe rather than what a reader needs to know — so a digest built on it inherits spin as fact even where nothing is invented.

Generalized: no vault content stands an abstract in for the source, and an evidence-boundary tag is not a laundering device — marking abstract-derived content `(inference)` does not make it honest.

When no full text is reachable, the digest slot carries the literal statement **"no full text available"**. Absence made legible is the honest summary; a metadata-only stub that silently reads as "nothing to say" is not.

## Considered Options

Abstract-derived digest disclosed as inference (rejected: the tag launders nothing, and this is the branch the shipped evidence-conventions text still permits — the reason this ADR exists rather than a prose fix). No digest at all (rejected: an unannotated item stays a metadata stub that orientation and gap analysis read nothing from). Extractive or NLP summarization from full text (rejected separately: salience is judgment and belongs to the authored lane; extractive output is statistical judgment dressed as machine trust).

## Consequences

Digest coverage is bounded by reachable full text. Until the full-text leg lands, the sanctioned route is reading the attachment directly via its Zotero storage path. A no-op is a legitimate outcome — a concise, searchable source may need no digest at all.

______________________________________________________________________

## 5. ADR 0008 — Claim anchors derive from content, never from render order

# Claim anchors derive from content, never from render order

Status: proposed (2026-08-23)

A claim's `^claim-id` derives from stable content — the Zotero annotation key where one exists, otherwise a hash of the quote — and never from its position in the rendered output. Managed regions are re-rendered whole, so an order-derived anchor would renumber on every regeneration and silently break every claim link pointing into it. Claim links are the vault's only global address for an assertion; an address that moves is not an address.

## Considered Options

Ordinal or sequential anchors, the obvious implementation (rejected: full re-render is the projection's normal mode, so every regeneration would invalidate links). A machine-owned claim ledger holding the mapping (deferred rather than rejected: it is the upgrade path if prose parsing becomes the bottleneck, and content-derived anchors are what make that upgrade retrofit-free).

## Consequences

Quote claims capture Web-Annotation-shaped context — the exact text plus short prefix and suffix — at extraction time, because it is nearly free then and unreconstructable later; the re-anchoring cascade that consumes it is deferred.

The **citekey half of the address is mutable by design, and its rename semantics are unsettled.** `citekey#^claim-id` is stable in its anchor half only: on a citekey rename, verified-event check strings hard-code the old address, and standing acknowledgments key on check-plus-target, so a rename silently lapses them — while rewriting the events would violate ADR 0002's never-rewritten history. Both horns break a record contract. This is named here rather than resolved, and settles before the first real citekey rename.

______________________________________________________________________

## 6. ADR 0001 — scope-bound sentence

Appended to `docs/adr/0001-vault-outlives-harness.md`, in the manner ADR 0003 already models:

> **Scope bound (2026-08-23):** the vault preserves the *record*, not the evidence artifacts. PDFs and snapshots live in Zotero storage, outside the git boundary — git is not the blob store — so artifact recoverability is delegated to the user's Zotero sync/backup, with doctor's persistent warning as the only compensating control. At solo scope this is a stated boundary, not a compliance control.

Why a sentence and not a seventh ADR: it narrows an existing decision rather than making a new one, and a reader who trusts "the vault outlives the harness" needs the exception where that promise is made, not one file away.

## 7. CONTEXT.md changes

**Line numbers below predate the 2026-08-23 dictionary cleanup** (34 entries → 28: *Synthesis note*, *System folder*, *Venue*, *Information flow*, *Project flow*, *Doctor* cut or folded) — locate each entry by content, not by line.

Projection rule applied throughout (ruled this session): **a term projects into the vault glossary if a vault note, folder, or field surfaces it to the researcher**; harness-operator vocabulary stays CONTEXT-only, as *Closing check* and *Doctor* already do.

**(a) Bibliography export — rewrite.** Current text states the superseded single-universe contract ("the citekey universe … that citations, filenames, and checks all join against").

> **Bibliography export**: The universe of items a citekey can name: the Better BibTeX auto-export at `system/bibliography.json`, written only by BBT — being in it is not yet being citable here.
> _Avoid_: bibliography file, reference list, citation universe (that is the evidence layer)

Projects: yes.

**(b) Acknowledgment — rewrite.** Current text overclaims exclusivity ("the only bypass any closed check has"); pre-commit's bypass is `--no-verify` and the publish gate's is a documented manual token.

> **Acknowledgment**: A human's standing, hash-scoped acceptance of a finding — the recorded decision that lets a check stand down without the finding being erased.
> _Avoid_: dismissal, override (an ack keeps the record; it never deletes)

Projects: yes. The bypasses themselves stay out — closing-set contents are spec material.

**(c) Synthesis layer — two-word fix.** The definition currently uses "topic pages", the exact phrase its own `_Avoid_` line bans.

> **Synthesis layer**: The LLM-maintained pages (`synthesis/`) that arrange claims across sources; freely rewritable because it asserts arrangement, not evidence.
> _Avoid_: atlas, wiki, topic pages

Projects: yes.

**(d) Citable — new term**, in *Evidence and claims*. The word is load-bearing in two existing entries and defined in neither.

> **Citable**: What a claim is allowed to cite: an item admitted in Zotero whose literature note exists in this vault — being in the library is not yet being citable here.
> _Avoid_: in the library, in the bibliography

Projects: yes — vault-operational, and the distinction is what ADR 0006 turns on.

**(e) Summary — new term, DEFERRED by author ruling 2026-08-23**: the name is ruled, the entry does not land until the step that authors the artifact ships (a glossary defines what exists). Ruling and the churn list live at `docs/superpowers/plans/2026-08-22-post-q-batch.md` Part 3; this is the held draft, for *Evidence and claims*, beside *Literature note*.

> **Summary**: The authored account of what a source says, written into its literature note's free prose from the source itself, never from its abstract.
> _Avoid_: digest, synopsis, abstract (that is the source's own, and never the basis for this), annotation (that is Zotero's highlight)

Projects: yes.

**Churn this name costs** (priced at zero per terminology.md §1, listed so it is not discovered later): `knowledge_harness/templates/vault/index.md:10` reads "daily activity log (summary: \[[log]\])" — the only *vault-facing* competing use, reword to "rolled up"; CONTEXT.md's *Log* entry says "summarized in root `log.md`", same reword; `knowledge_harness/okf.py:1` and `inbox.summary()` are dev-facing (T7) and may stay or rename at the implementer's discretion. Third-party surfaces are untouched by rule: arXiv's `<summary>` element and PubMed's `eSummary` endpoint keep their own names, and our boundary already translates arXiv's into `abstract` — which is exactly the disambiguation this term needs.

## 8. terminology.md rows

**Naming walk for the authored account (re-run 2026-08-23 after the ecosystem sweep, superseding the same-day `digest` adoption).** The first walk stopped at T6/T8 without testing T4 or the ecosystem, which §2 does not permit. Corrected walk, under the author's ruling that **churn is not a cost and the user-facing term takes precedence** (§1; tie-breaker 4, surface fit is absolute):

T1 OKF is silent — its `description` is a frontmatter field, not body prose. T2 toolchain surfaces name the *container*, not this artifact (ZotLit's "note" template body, Zotero's child notes, CSL's `note`/`annote`). T4 offers *summary*, *synopsis*, *précis*. T6 is where the concept actually lives, and it is near-unanimous: **`## Summary` / "source summary page"** across paperclip (79k★), claude-obsidian (11.3k★), SamurAIGPT/llm-wiki-agent (3.4k★), sdyckjq-lab/llm-wiki-skill (2.4k★), obsidian-llm-wiki-local (809★), swarmvault (666★), pi-llm-wiki (524★), tonbistudio/llm-wiki (247★), wiki-skills (179★); the llm-wiki gist itself writes "a summary page in the wiki". T4 and T6 agree on the same word.

**Adopted: `summary` (T4 confirmed by T6).** *Page* is dropped from the borrowed phrase because it names the file, and that slot is `literature note`.

Declined: **digest** — the only ecosystem instance is a 9-star repo (`WeAgentAI/LLM-Wiki`, "Source-digest template"), the in-repo anchor names another system's output, and the hash sense is stdlib (`hexdigest()`), so a residual collision could never be fully cleared. **synopsis** — clean but has no user-facing currency, which the ruling makes decisive. **précis** — same, plus it implies a proportional in-order restatement, which an `(inference)`-tagged region is not. **annotation** — exact in annotated-bibliography practice, fatal against Zotero's highlight sense.

**Identifier inventory:** `skipped_digest` → `skipped_sha256` — no longer a collision fix (see §9), retained as a precision improvement in the house `-sha256` form.

## 9. Post-Q batch item

> **Rename `skipped_digest` → `skipped_sha256`** (terminology ruling 2026-08-23): frees *digest* for the authored account of a source, and names the algorithm the way `fixity-sha256`/`managed-sha256` already do. Sites: `knowledge_harness/factcheck.py:165,192`; `skills/factcheck-draft/SKILL.md:28,64` (user-visible JSON field); `tests/test_factcheck.py:199-227`. Invalidates `knowledge_harness/factcheck.py.manifest.json` (`module_hash` + `source_sha256`) — one module's mutation re-baseline, not a wholesale one.

## 10. Already applied this session

Foundation spec §4 and §10, on the author's ruling that "rejected permanently" was stale: two-way Zotero↔vault sync is **deferred behind the same Zotero 10 local-writes gate** as content write-back, with the absence of prior art recorded as why it is not attempted now rather than as a permanent ban. The deferred register gained the matching entry. No ADR — a deferred item is not a decision to record.

## 11. Rejected and deferred, with reasons

Recorded so they are not re-litigated from scratch.

- **Narrowing *Import* to exclude the authored step** — refuted. The entry's head clause already scopes "never authored" to the machine projection, and the digest lives in the free region the projection preserves rather than renders. "Capture" is also already spent on *Inbox*, and the shipped step is named *Catalog*.
- **Qualifying *Admission* as necessary-but-not-sufficient** — refuted. "The only way anything becomes citable" is a necessity claim; tier-2 adds a second necessary condition, which does not falsify it. Tier-2 surfaces as *Citable* instead.
- **A *Human gate* glossary entry** — dropped by the author: strip the rule and what remains is a dictionary definition. ADR 0004 owns the rule.
- **CLI-not-MCP as an ADR** — dropped: shipping deterministic scripts behind skills is common practice, so it fails the surprising test even though it is hard to reverse.
- **Two-way sync as an ADR** — dropped: it is a deferred item behind a version gate, not a decision.
- **Dependency discipline as an ADR** — deferred with a named trigger: write it when the contract-match rule survives a third contested admission, or at the architecture deepening pass, whichever comes first.
- **Library-as-curated-search-space** — dropped: situational, and ruled then amended inside 24 hours with the migration still in flight.
- **The ingest generator ruling** (LLM-authored claim-grammar digest, no extractive summarizer) — dropped as temporary; its full-text half is ADR 0007, which stands on its own.
- **Evidence-layer-is-projection** and **deterministic-only closure** — stay parked per spec §10: the control model they entangle with is still moving, as the 2026-08-22 gate-doctrine amendment itself demonstrates.
- **Provenance-travels-with-the-claim** — refuted as an ADR: it is schema shape, already fully stated in spec §5.

## 12. AGENTS.md — already resolved by the author

The contradiction this section proposed to fix is gone: the author removed the whole sentence ("`research/`, `analysis/`, completed plans, and accepted ADRs stand as written — content, internal paths, and file location") from AGENTS.md while this document was being written. ADR governance is process, and process lives in the `domain-modeling` skill or the user's own CLAUDE.md/AGENTS.md, not in this repo's project-detail file; the skill's template already carries the revision vocabulary (`Status: proposed | accepted | deprecated | superseded by ADR-NNNN`). `research/`, `analysis/`, and completed plans stand as the author's stated temporary-file classes rather than as a repo-frozen set.

**Nothing is proposed here.** §6's scope-bound sentence on ADR 0001 is not an exception to any written rule.
