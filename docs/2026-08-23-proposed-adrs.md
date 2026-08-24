# Proposed ADRs and CONTEXT.md changes

Status: **PROPOSAL — nothing here has landed.** ADR files are written only after approval of the final version (author ruling, this session). Format follows the `domain-modeling` skill's ADR template; the three-part test (hard to reverse / surprising without context / real trade-off) gates every candidate below.

**How the sources were used.** The foundation spec, the slice findings, and the audit reports are read here as a log of what happened and what broke — a source of candidate decisions and of concrete failures worth citing. They are not treated as authority: nothing below is justified by a document saying so. Each ADR stands on the failure it prevents and the alternative it rejects, and should be readable by someone who has never opened those files.

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

## 1. ADR 0004 — Rubber stamps are defects, not controls

# Rubber stamps are defects, not controls

Status: proposed

**Place a human gate only where the answer can differ from the last time.** A confirmation that is always yes certifies nothing and teaches the person to click without reading, and that habit travels to the gates that matter — which is why a warn queue whose findings are mostly not actionable is a defect to tune or demote, not a cost of doing business. Admitting a corpus of 170 already-reviewed sources one at a time would have produced 170 identical answers and a habit; the same import, reviewed as a batch, turned up 17 real misclassifications.

Where the judgment covers a whole list, the human act is the decision: one approval, the list's hash stored beside it, the machine performing the entries. Where judgment is per item, the per-item gate stays.

## Considered Options

Confirm every item (rejected: an approval nobody can withhold certifies nothing, and it spends the attention the live gates need). Admit in bulk with no record (rejected: a trust boundary crossed without a record is not one).

## 2. ADR 0005 — Absence is not a pass

**Option A (recommended): its own ADR, referencing 0002.** Draft:

# Absence is not a pass

Status: proposed

**A machine trust tier requires at least one check that ran and passed**, and a value the harness does not have stays out of the record. Where the answer is unknown, the record says so: an honest four-state result, or an absent field with a reason in the review inbox.

Both halves come from live failures. A note with no identifiers, no quotes, and no verified events reached the top machine tier, because nothing had been checked, so nothing had failed, so "every applicable check passed" was true over an empty set. And three writers filled gaps by invention: a year-only date became January 1st, the string `"unresolved"` went into a hash field and then anchored an acknowledgment, and a missing title became the citekey.

## Considered Options

Let set logic supply the floor (rejected: the empty applicable-check set is exactly the case that deserves "unverified", and vacuous truth answers the opposite). Write placeholders to keep pipelines moving (rejected: the placeholder escapes — `"unresolved"` became what acknowledgments scoped to, so they scoped to a constant).

## Consequences

Some items will never reach a machine tier; that is the honest outcome rather than a gap to close. Every writer of durable frontmatter needs a branch for "we do not have this". This extends ADR 0002 and does not amend it.

**Option B: fold into ADR 0002** as two sentences — a floor on tier derivation, and a rule against invented values on durable writes. No new file; the cost is that the failures above lose the place explaining why each rule exists.

## 3. ADR 0006 — A source becomes citable here when its literature note exists

# A source becomes citable here when its literature note exists

Status: proposed

**Two questions, two answers.** The bibliography export says what a citekey names; membership in `literatures/` says what this vault may cite. The citekey check asks the second question, because the reference library holds every project the researcher has ever worked on — a citekey borrowed from an unrelated project resolves against the whole-library export, so a citation to a paper this vault never imported passed its check and could publish.

A failing citation has one remedy: import the source, which writes the note, which makes the check pass — and the new note files its own evidence-layer finding at commit, like any import. Membership has one source of truth, the folder itself, so no separate list of citable keys exists to drift.

## Considered Options

Treat the export as both universes (rejected: it cannot tell a legitimate citation from one that leaked in from another project). Keep a curated allowlist file (rejected: two records of one fact, and the file loses). Export a per-project collection instead (rejected: that inserts curation between admission and the key universe, and it is a performance idea rather than a trust boundary).

## Consequences

An import is what confers citability, so this check rests on the rule that only the bridge writes into `literatures/`. Screening stays a separate axis: an excluded or superseded note keeps its place in the folder under ADR 0003, and the screening-state check is what keeps it out of a draft.

## 4. ADR 0007 — A summary is written from full text or not at all

# A summary is written from full text or not at all

Status: proposed

**Write the summary from the full text. When the full text is unreachable, write "no full text available" and stop.** An abstract cannot supply the methods, conditions, and magnitudes a summary states, so a summary drawn from one attributes invented specifics to the source under its citekey — a fabricated fact, and an `(inference)` tag does not repair it. A second reason survives even where nothing is invented: the abstract is where authors sell the work, so a summary built on it inherits the pitch as fact.

The literal sentence matters, because a stub that says nothing reads as "this source had nothing to say".

## Considered Options

Write from the abstract and disclose it (rejected: disclosure does not repair invention, and the tag becomes a laundering device). Write nothing at all (rejected: the source stays a metadata stub that orientation and gap analysis read nothing from). Extract sentences mechanically from the full text (rejected: choosing what matters is judgment, and extractive output would wear machine-trust clothing while making it).

## Consequences

Writing no summary is a legitimate outcome for a source that is short and searchable.

## 5. ADR 0008 — Claim anchors derive from content, never from render order

# Claim anchors derive from content, never from render order

Status: proposed

**An anchor derives from the claim's own content**: the Zotero annotation key where one exists, otherwise a hash of the quote. Managed regions re-render whole, so an anchor derived from position — the third claim in the note — would renumber everything below a newly added annotation, and every link into that region would land on the wrong claim. Deriving from content, re-rendering yields the same anchors for the same claims, and a link written a year ago still points at what it named.

## Considered Options

Sequential anchors, the obvious implementation (rejected: re-render is the normal mode, so the anchors would move constantly). A machine-owned ledger mapping claims to stable ids (deferred rather than rejected: it is the upgrade path if parsing prose becomes the bottleneck, and content-derived anchors are what let it arrive later without rewriting history).

## Consequences

Quote claims record the exact text plus a short prefix and suffix at extraction time, because that context is nearly free then and impossible to reconstruct afterwards.

## 6. ADR 0001 — scope-bound sentence (APPLIED)

Approved and landed 2026-08-23; the text below is what the file carries, with no date marker, per the ruling that ADRs carry no history.

> **Scope bound:** the vault preserves the *record*, not the evidence artifacts. PDFs and snapshots live in Zotero storage, outside the git boundary — git is not the blob store — so artifact recoverability is delegated to the user's Zotero sync/backup, with doctor's persistent warning as the only compensating control. At solo scope this is a stated boundary, not a compliance control.

Why a sentence and not a seventh ADR: it narrows an existing decision rather than making a new one, and a reader who trusts "the vault outlives the harness" needs the exception where the promise is made.

## 7. CONTEXT.md changes

**Line numbers below predate the 2026-08-23 dictionary cleanup** (34 entries → 28: *Synthesis note*, *System folder*, *Venue*, *Information flow*, *Project flow*, *Doctor* cut or folded) — locate each entry by content, not by line.

Projection rule applied throughout (ruled this session): **a term projects into the vault glossary if a vault note, folder, or field surfaces it to the researcher**; harness-operator vocabulary stays CONTEXT-only, as *Closing check* and *Doctor* already do.

**(a) Bibliography export — rewrite.** Current text states the superseded single-universe contract ("the citekey universe … that citations, filenames, and checks all join against").

> **Bibliography export**: The universe of items a citekey can name: the Better BibTeX auto-export at `system/bibliography.json`, written only by BBT.
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

> **Citable**: What a claim is allowed to cite: an item admitted in Zotero whose literature note exists here and is neither excluded nor superseded — being in the library is not yet being citable here.
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

## 9. Post-Q batch item (LANDED — superseded here)

Task 22 of `docs/superpowers/plans/2026-08-22-post-q-batch.md` is committed and carries the corrected motivation. The rationale drafted here — that the rename frees *digest* for the authored account — died with §8's walk, which adopted *summary*. The landed ruling reads:

> **RULING — name the value what it is.** The report field holds a SHA-256 hex string, so it takes the algorithm's own name, in the form `fixity-sha256` and `managed-sha256` already use where the value is durable.
>
> **This is a precision fix, not a collision fix.** … nothing collides and nothing downstream waits on this task. … **If the implementer hits any friction in Step 4, drop the task** rather than spend the instrument-freeze window on it.

Nothing further is proposed in this section; read the plan.

## 10. Already applied this session

An edit to the foundation spec, on the author's ruling that its "rejected permanently" wording was stale: two-way Zotero↔vault sync is **deferred behind the same Zotero 10 local-writes gate** as content write-back, with the absence of prior art recorded as why it is not attempted now rather than as a permanent ban. The deferred register gained the matching entry. No ADR — a deferred item is not a decision to record.

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
- **Evidence-layer-is-projection** and **deterministic-only closure** — not yet decisions. Both are entangled with how much the system decides for the user versus asking, and that is still moving: the gate doctrine changed once already while this document was being written. An ADR written on top of a moving premise records the premise, not a decision.
- **Provenance-travels-with-the-claim** — **reinstated 2026-08-23** after the earlier rejection failed re-examination; drafted as ADR 0009 in §13.

## 12. AGENTS.md — already resolved by the author

The contradiction this section proposed to fix is gone: the author removed the whole sentence ("`research/`, `analysis/`, completed plans, and accepted ADRs stand as written — content, internal paths, and file location") from AGENTS.md while this document was being written. ADR governance is process, and process lives in the `domain-modeling` skill or the user's own CLAUDE.md/AGENTS.md, not in this repo's project-detail file; the skill's template already carries the revision vocabulary (`Status: proposed | accepted | deprecated | superseded by ADR-NNNN`). `research/`, `analysis/`, and completed plans stand as the author's stated temporary-file classes rather than as a repo-frozen set.

**Nothing is proposed here.** §6's scope-bound sentence on ADR 0001 is not an exception to any written rule.

## 13. ADR 0009 — Provenance travels with the claim (reinstated)

Rejected earlier in this document as "record shape, not a decision". That was wrong on two prongs. Frontmatter-only attribution was a real alternative — it is what most note systems do — and a reader meeting inline fields in their own prose will ask why the notes are full of syntax. Drafted here rather than argued in the rejected list:

# Provenance travels with the claim

Status: proposed

**Every claim carries its own evidence-boundary tag, citation, and anchor on its own line**, never in the note's frontmatter. A claim gets copied — from a literature note into a synthesis page, from synthesis into a draft — and whatever is not on the line does not travel with it. Attribution held at the note level survives exactly one hop, and the hop is the moment the claim most needs it.

## Considered Options

Frontmatter-only attribution (rejected: cleaner prose, and the tag is severed by the first relay — a quote lands in a draft with nothing saying it is a quote). A side-file mapping claims to provenance (rejected: the mapping is what breaks, and it breaks silently).

## Consequences

Notes carry visible field syntax in their prose, which is the cost paid for relay-safe attribution. Anything that rewrites a claim line must preserve its fields, which is why machine-written verification markers are stamped onto the claim rather than recorded beside it.
